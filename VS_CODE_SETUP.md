# VS Code Setup Guide for Deepfake Detection Application

This guide provides detailed steps to set up and run the Deepfake Detection application in Visual Studio Code.

## Prerequisites

1. Install [Visual Studio Code](https://code.visualstudio.com/download)
2. Install [Python](https://www.python.org/downloads/) (version 3.9 or higher)
3. Get a [Google Gemini API key](https://ai.google.dev/)

## Step-by-Step Setup Instructions

### 1. Clone or Download the Project

- Download the project as a ZIP file and extract it to a folder of your choice, or
- Clone the repository if available with Git

### 2. Open the Project in VS Code

1. Open VS Code
2. Go to File → Open Folder...
3. Navigate to and select the project folder
4. Click "Select Folder"

### 3. Set Up Python Environment

1. Open a terminal in VS Code (Terminal → New Terminal)
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - On Windows:
     ```
     .\venv\Scripts\activate
     ```
   - On Linux/Mac:
     ```
     source venv/bin/activate
     ```
   You should see `(venv)` prefix in your terminal prompt, indicating the virtual environment is active

### 4. Install Dependencies

Run the following command to install all required packages:
```
pip install -r dependencies.txt
```

Alternatively, you can install the packages individually:
```
pip install flask flask-sqlalchemy google-generativeai pillow python-dotenv werkzeug requests
```

### 5. Configure Environment Variables

1. Create a `.env` file in the root directory of the project:
   - Copy the `.env.example` to `.env`:
     - Windows: `copy .env.example .env`
     - Linux/Mac: `cp .env.example .env`
   
2. Edit the `.env` file:
   - Right-click on the `.env` file in VS Code Explorer and select "Open"
   - Add your Gemini API key:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```
   - Replace `your_api_key_here` with your actual Gemini API key
   - Add a session secret key (optional but recommended):
     ```
     SESSION_SECRET=your_secret_key_here
     ```

### 6. Create Required Folders

Make sure you have an `uploads` folder in the project root:
```
mkdir uploads
```

### 7. Run the Application

1. Make sure your terminal still has the virtual environment activated (`(venv)` prefix)
2. Run the application:
   ```
   python main.py
   ```
3. You should see output indicating that the application is running, with a URL (typically http://localhost:5000)

### 8. Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

## Troubleshooting Common Issues

### ModuleNotFoundError: No module named 'dotenv'

If you see this error when running the application:
```
ModuleNotFoundError: No module named 'dotenv'
```

Run:
```
pip install python-dotenv
```

### Error During Analysis - No API_KEY found

If you see this error when analyzing images:
```
Error During Analysis
No API_KEY or ADC found.
```

Check that:
1. You've created the `.env` file correctly
2. The Gemini API key is correctly set in the `.env` file
3. The `.env` file is in the same directory as `main.py`

### VS Code Python Interpreter Selection

If VS Code is not using your virtual environment Python:

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type "Python: Select Interpreter" and select it
3. Choose the Python interpreter from your virtual environment (it should have "venv" in the name)

### Other Issues

If you encounter any other issues:
1. Make sure all required packages are installed
2. Check console output for specific error messages
3. Verify your API key is valid and has access to the Gemini API
4. Ensure image files are in supported formats (JPG, PNG, or GIF)