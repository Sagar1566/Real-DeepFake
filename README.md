# Deepfake Image Detection

A web application leveraging Google's Gemini API to perform advanced deepfake detection by comparing uploaded images with reference images.

## Features

- Upload and compare two images (original reference and suspected deepfake)
- AI-powered analysis using Google's Gemini API
- Detailed explanation of the analysis results
- Confidence level assessment
- Cross-platform compatible (works on Windows, Linux, and Mac)

## Prerequisites

- Python 3.9 or higher
- A Google Gemini API key (https://ai.google.dev/)

## Installation

### Running in VS Code

1. Extract the zip file to a folder
2. Open the folder in VS Code
3. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
4. Activate the virtual environment:
   - Windows: `.\venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
5. Install dependencies:
   ```bash
   pip install -r dependencies.txt
   ```
6. Set up environment variables:
   - Copy the `.env.example` file to `.env`: 
     - Windows: `copy .env.example .env`
     - Linux/Mac: `cp .env.example .env`
   - Open the `.env` file and replace the placeholder values with your actual credentials:
     - Add your Gemini API key: `GEMINI_API_KEY=your_api_key_here`
     - You can also set `SESSION_SECRET=your_secret_key` for session security

7. Run the application:
   ```bash
   python main.py
   ```
8. Open your browser and navigate to `http://localhost:5000`

## How to Use

1. Open the application in your web browser
2. Upload an original reference image (the known authentic image)
3. Upload a suspected deepfake image (the image you want to analyze)
4. Click "Analyze Images"
5. View the analysis results, including:
   - Whether the second image appears to be a deepfake
   - Confidence level of the determination
   - Detailed analysis explaining the reasoning

## Troubleshooting

- If you encounter any path-related errors when using the app on Windows, the application includes robust path handling that should resolve most issues automatically.
- If you receive an error about missing the Gemini API key, make sure you've correctly set it in your environment or .env file.
- If images fail to display on the results page, try uploading smaller images (the app will automatically resize large images).

## License

This project is MIT licensed.