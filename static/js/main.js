// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get file input elements
    const originalInput = document.getElementById('original_image');
    const suspectedInput = document.getElementById('suspected_image');
    
    // Get preview elements
    const originalPreview = document.getElementById('original-preview');
    const suspectedPreview = document.getElementById('suspected-preview');
    
    // Get form and loading indicator
    const uploadForm = document.getElementById('upload-form');
    const analyzeBtn = document.getElementById('analyze-btn');
    const loadingIndicator = document.getElementById('loading-indicator');
    
    // Add event listeners for file inputs
    if (originalInput) {
        originalInput.addEventListener('change', function() {
            displayPreview(this, originalPreview);
        });
    }
    
    if (suspectedInput) {
        suspectedInput.addEventListener('change', function() {
            displayPreview(this, suspectedPreview);
        });
    }
    
    // Add event listener for form submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', function() {
            // Validate form before submission
            if (validateForm()) {
                // Show loading indicator and disable button
                if (loadingIndicator) loadingIndicator.classList.remove('d-none');
                if (analyzeBtn) {
                    analyzeBtn.disabled = true;
                    analyzeBtn.innerHTML = '<div class="spinner-border spinner-border-sm me-2" role="status"></div>Analyzing...';
                }
                return true;
            } else {
                return false;
            }
        });
    }
    
    /**
     * Display image preview when a file is selected
     */
    function displayPreview(input, previewElement) {
        if (!input.files || !input.files[0]) {
            // Clear preview if no file selected
            previewElement.innerHTML = '<i class="fas fa-image preview-placeholder"></i>';
            return;
        }
        
        const file = input.files[0];
        
        // Check file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            alert('File is too large. Maximum size is 10MB.');
            input.value = '';
            previewElement.innerHTML = '<i class="fas fa-image preview-placeholder"></i>';
            return;
        }
        
        // Check file type
        const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/jpg'];
        if (!validTypes.includes(file.type)) {
            alert('Invalid file type. Please upload a JPG, JPEG, PNG or GIF.');
            input.value = '';
            previewElement.innerHTML = '<i class="fas fa-image preview-placeholder"></i>';
            return;
        }
        
        // Create preview
        const reader = new FileReader();
        reader.onload = function(e) {
            previewElement.innerHTML = `<img src="${e.target.result}" class="preview-image" alt="Preview">`;
        };
        reader.readAsDataURL(file);
    }
    
    /**
     * Validate form before submission
     */
    function validateForm() {
        // Check if both files are selected
        if (!originalInput.files || !originalInput.files[0]) {
            alert('Please select an original reference image.');
            return false;
        }
        
        if (!suspectedInput.files || !suspectedInput.files[0]) {
            alert('Please select a suspected deepfake image.');
            return false;
        }
        
        return true;
    }
});
