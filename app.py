import os
import logging
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import base64
import requests
import json
from PIL import Image
import io
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "deepfake-detection-secret-key")

# Configure upload settings
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB limit

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Configure Gemini API
# Check for both potential API key environment variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# Use either key, with GEMINI_API_KEY taking precedence
api_key = GEMINI_API_KEY or GOOGLE_API_KEY

if not api_key:
    logger.warning("API key not set. Please set either GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")
    logger.warning("The application will not function without a valid API key.")
else:
    logger.info("API key found. Configuring Gemini API.")

# Configure the API with whatever key we found
genai.configure(api_key=api_key)

def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def encode_image(image_path):
    """Encode image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def resize_image_if_needed(file_path, max_size=(1024, 1024)):
    """Resize image if it's too large for the API"""
    try:
        # Normalize the path to handle OS-specific path separators
        file_path = os.path.normpath(file_path)
        
        logger.info(f"Checking if image needs resizing: {file_path}")
        
        img = Image.open(file_path)
        if img.width > max_size[0] or img.height > max_size[1]:
            img.thumbnail(max_size, Image.LANCZOS)
            img.save(file_path)
            logger.info(f"Image resized to {img.size}")
        else:
            logger.info(f"No resize needed, image is {img.size}")
    except Exception as e:
        logger.error(f"Error resizing image: {e}")

def analyze_images_with_gemini(original_path, suspected_path):
    """
    Use Google's Gemini API to analyze if the second image is a deepfake
    compared to the first (original) image
    """
    try:
        # Normalize paths to prevent OS-specific path separator issues
        original_path = os.path.normpath(original_path)
        suspected_path = os.path.normpath(suspected_path)
        
        logger.info(f"Analyzing images from: {original_path} and {suspected_path}")
        
        # Configure the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Load images
        original_img = Image.open(original_path)
        suspected_img = Image.open(suspected_path)
        
        # Prepare prompt for Gemini
        prompt = """
        Analyze these two images carefully:
        Image 1 is provided as the reference/original image.
        Image 2 is a suspected deepfake or manipulated version.
        
        IMPORTANT: First determine if these are images of the same person or different people.
        If they are clearly different people, immediately identify this as a deepfake or manipulation.
        
        Perform a detailed analysis comparing them:
        1. Check if the faces appear to be the same person - different people means it's a deepfake
        2. Identify signs of manipulation in the second image
        3. Check for inconsistencies in lighting, shadows, and reflections
        4. Look for unnatural edges, blurring, or artifacts
        5. Examine facial proportions and features (eyes, nose, mouth, jawline)
        6. Assess texture inconsistencies
        
        Conclude with: 
        1. A determination if the second image appears to be a deepfake or manipulated (yes/no)
        2. Confidence level (low/medium/high)
        3. Brief explanation of your reasoning
        
        If the images show completely different people, the answer MUST be "yes" (it is a deepfake) with high confidence.
        
        Format your response with clear headings and be as specific as possible.
        """
        
        # Generate content with Gemini
        response = model.generate_content([prompt, original_img, suspected_img])
        
        # Process response
        analysis = response.text
        
        # Extract determination
        is_deepfake = False
        confidence = "Medium"  # Default to Medium instead of Unknown
        
        # Check for keywords that indicate different people or deepfake
        text_lower = analysis.lower()
        
        # Strong indicators of different people/deepfake
        if any(phrase in text_lower for phrase in [
            "different people", 
            "not the same person",
            "completely different",
            "two different individuals",
            "different individuals"
        ]):
            is_deepfake = True
            confidence = "High"
        # Indicators of same person (non-deepfake)
        elif "same person" in text_lower and "not a deepfake" in text_lower:
            is_deepfake = False
            confidence = "High" if "high confidence" in text_lower else "Medium"
        else:
            # Fall back to yes/no determination
            if "yes" in text_lower and ("deepfake" in text_lower or "manipulated" in text_lower):
                is_deepfake = True
            elif "no" in text_lower and "not a deepfake" in text_lower:
                is_deepfake = False
            
            # Extract confidence
            if "high confidence" in text_lower:
                confidence = "High"
            elif "medium confidence" in text_lower:
                confidence = "Medium"
            elif "low confidence" in text_lower:
                confidence = "Low"
        
        return {
            "is_deepfake": is_deepfake,
            "confidence": confidence,
            "analysis": analysis
        }
    
    except Exception as e:
        logger.error(f"Error analyzing images: {e}")
        return {
            "error": str(e),
            "is_deepfake": None,
            "confidence": "Medium",  # Default to Medium even on error
            "analysis": f"Error during analysis: {str(e)}"
        }

@app.route('/')
def index():
    """Render the main page with upload form"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads and process images"""
    # Check if both files were submitted
    if 'original_image' not in request.files or 'suspected_image' not in request.files:
        flash('Both images are required', 'danger')
        return redirect(request.url)
    
    original_file = request.files['original_image']
    suspected_file = request.files['suspected_image']
    
    # Check if filenames are empty
    if original_file.filename == '' or suspected_file.filename == '':
        flash('No selected files', 'danger')
        return redirect(request.url)
    
    # Check if files are valid
    if not (original_file and allowed_file(original_file.filename) and
            suspected_file and allowed_file(suspected_file.filename)):
        flash('Invalid file types. Please use jpg, jpeg, png, or gif.', 'danger')
        return redirect(request.url)
    
    try:
        # Save files with secure filenames
        original_filename = secure_filename(original_file.filename)
        suspected_filename = secure_filename(suspected_file.filename)
        
        # Check if we're running on Windows or Linux/Mac
        is_windows = os.name == 'nt'
        path_separator = '\\' if is_windows else '/'
        
        # Create folder path with correct separators
        upload_folder = app.config['UPLOAD_FOLDER']
        
        # Print debug info about the paths
        logger.info(f"Current platform: {os.name}, using separator: {path_separator}")
        logger.info(f"Upload folder: {upload_folder}")
        
        # Ensure the upload directory exists (using raw strings to avoid escape issues)
        os.makedirs(upload_folder, exist_ok=True)
        
        # Create file paths with explicit separators
        original_path = os.path.join(upload_folder, f"original_{original_filename}")
        suspected_path = os.path.join(upload_folder, f"suspected_{suspected_filename}")
        
        # Final normalization to ensure consistency
        original_path = os.path.normpath(original_path)
        suspected_path = os.path.normpath(suspected_path)
        
        logger.info(f"Saving original file to: {original_path}")
        logger.info(f"Saving suspected file to: {suspected_path}")
        
        # Save files
        original_file.save(original_path)
        suspected_file.save(suspected_path)
        
        # Resize images if needed
        resize_image_if_needed(original_path)
        resize_image_if_needed(suspected_path)
        
        # Analyze images using Gemini API
        results = analyze_images_with_gemini(original_path, suspected_path)
        
        # Get base filenames for more reliable storage in session
        original_basename = os.path.basename(original_path)
        suspected_basename = os.path.basename(suspected_path)
        
        # Save results to session
        session['analysis_results'] = results
        
        # Store both full path and basename to provide fallback options
        session['original_path'] = original_path
        session['suspected_path'] = suspected_path
        session['original_basename'] = original_basename
        session['suspected_basename'] = suspected_basename
        
        logger.info(f"Stored in session - original: {original_path}, basename: {original_basename}")
        logger.info(f"Stored in session - suspected: {suspected_path}, basename: {suspected_basename}")
        
        return redirect(url_for('results'))
    
    except Exception as e:
        logger.error(f"Error processing upload: {e}")
        flash(f'Error processing upload: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/results')
def results():
    """Display analysis results"""
    if 'analysis_results' not in session:
        flash('No analysis results available', 'warning')
        return redirect(url_for('index'))
    
    # Get results from session
    results = session['analysis_results']
    original_path = session.get('original_path', '')
    suspected_path = session.get('suspected_path', '')
    
    # Get basenames for fallback
    original_basename = session.get('original_basename', '')
    suspected_basename = session.get('suspected_basename', '')
    
    logger.info(f"Retrieved from session - original path: {original_path}")
    logger.info(f"Retrieved from session - suspected path: {suspected_path}")
    logger.info(f"Retrieved from session - original basename: {original_basename}")
    logger.info(f"Retrieved from session - suspected basename: {suspected_basename}")
    
    # Read image files for display
    original_image = None
    suspected_image = None
    
    try:
        # Check platform and normalize paths
        is_windows = os.name == 'nt'
        logger.info(f"Reading images on platform: {os.name}")
        
        # Normalize paths again to ensure consistency
        original_path = os.path.normpath(original_path)
        suspected_path = os.path.normpath(suspected_path)
        
        logger.info(f"Attempting to read original image from: {original_path}")
        logger.info(f"Attempting to read suspected image from: {suspected_path}")
        
        # Check if the paths exist
        # Try multiple approaches to find the original image
        image_found = False
        
        # Try 1: Direct path from session
        if os.path.exists(original_path):
            logger.info(f"Original image found at {original_path}")
            with open(original_path, 'rb') as f:
                original_image = base64.b64encode(f.read()).decode('utf-8')
            image_found = True
        
        # Try 2: Using basename in uploads folder
        if not image_found:
            fallback_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(original_path))
            logger.info(f"Trying fallback path: {fallback_path}")
            if os.path.exists(fallback_path):
                with open(fallback_path, 'rb') as f:
                    original_image = base64.b64encode(f.read()).decode('utf-8')
                logger.info("Found original image using path basename fallback")
                image_found = True
        
        # Try 3: Using stored basename
        if not image_found and original_basename:
            fallback_path = os.path.join(app.config['UPLOAD_FOLDER'], original_basename)
            logger.info(f"Trying stored basename fallback: {fallback_path}")
            if os.path.exists(fallback_path):
                with open(fallback_path, 'rb') as f:
                    original_image = base64.b64encode(f.read()).decode('utf-8')
                logger.info("Found original image using stored basename fallback")
                image_found = True
        
        if not image_found:
            logger.error("Could not find original image using any available method")
        
        # Same approach for the suspected image
        image_found = False
        
        # Try 1: Direct path from session
        if os.path.exists(suspected_path):
            logger.info(f"Suspected image found at {suspected_path}")
            with open(suspected_path, 'rb') as f:
                suspected_image = base64.b64encode(f.read()).decode('utf-8')
            image_found = True
        
        # Try 2: Using basename in uploads folder
        if not image_found:
            fallback_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(suspected_path))
            logger.info(f"Trying fallback path: {fallback_path}")
            if os.path.exists(fallback_path):
                with open(fallback_path, 'rb') as f:
                    suspected_image = base64.b64encode(f.read()).decode('utf-8')
                logger.info("Found suspected image using path basename fallback")
                image_found = True
        
        # Try 3: Using stored basename
        if not image_found and suspected_basename:
            fallback_path = os.path.join(app.config['UPLOAD_FOLDER'], suspected_basename)
            logger.info(f"Trying stored basename fallback: {fallback_path}")
            if os.path.exists(fallback_path):
                with open(fallback_path, 'rb') as f:
                    suspected_image = base64.b64encode(f.read()).decode('utf-8')
                logger.info("Found suspected image using stored basename fallback")
                image_found = True
        
        if not image_found:
            logger.error("Could not find suspected image using any available method")
    except Exception as e:
        logger.error(f"Error reading image files: {e}")
    
    return render_template('results.html', 
                           results=results,
                           original_image=original_image,
                           suspected_image=suspected_image)

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file size too large error"""
    flash('File too large. Maximum size is 10MB.', 'danger')
    return redirect(url_for('index')), 413

@app.errorhandler(500)
def server_error(error):
    """Handle server errors"""
    logger.error(f"Server error: {error}")
    flash('Server error occurred. Please try again later.', 'danger')
    return redirect(url_for('index')), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
