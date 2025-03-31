#!/usr/bin/env python3
"""
Project Structure Verification Script

This script checks if all required files and directories exist in the project,
and provides meaningful feedback about what might be missing.
"""

import os
import sys

def check_structure():
    """Check if all required files and directories exist."""
    required_files = [
        'main.py',
        'app.py',
        '.env',
        'dependencies.txt',
    ]
    
    required_dirs = [
        'uploads',
        'templates',
        'static',
    ]
    
    template_files = [
        'templates/index.html',
        'templates/results.html',
    ]
    
    static_files = [
        'static/css/custom.css',
        'static/js/main.js',
    ]
    
    missing_files = []
    missing_dirs = []
    
    # Check required files
    for file in required_files:
        if not os.path.isfile(file):
            missing_files.append(file)
    
    # Check required directories
    for directory in required_dirs:
        if not os.path.isdir(directory):
            missing_dirs.append(directory)
    
    # Check template files if templates directory exists
    if 'templates' not in missing_dirs:
        for file in template_files:
            if not os.path.isfile(file):
                missing_files.append(file)
    
    # Check static files if static directory exists
    if 'static' not in missing_dirs:
        for file in static_files:
            if not os.path.isfile(file):
                missing_files.append(file)
    
    # Check .env file contents
    env_issues = []
    if '.env' not in missing_files:
        try:
            with open('.env', 'r') as f:
                env_content = f.read()
                if 'GEMINI_API_KEY' not in env_content:
                    env_issues.append("Missing GEMINI_API_KEY in .env file")
                if 'SESSION_SECRET' not in env_content:
                    env_issues.append("Missing SESSION_SECRET in .env file (optional but recommended)")
        except Exception as e:
            env_issues.append(f"Error reading .env file: {str(e)}")
    
    # Print results
    if not missing_files and not missing_dirs and not env_issues:
        print("✅ All required files and directories exist!")
        print("\nIf you're still experiencing issues, check:")
        print("1. Python packages are installed correctly")
        print("2. GEMINI_API_KEY in .env is valid")
        print("3. Virtual environment is activated")
        return True
    else:
        print("❌ Some required files or directories are missing:")
        
        if missing_dirs:
            print("\nMissing Directories:")
            for directory in missing_dirs:
                print(f"  - {directory}")
            print("\nRun these commands to create missing directories:")
            for directory in missing_dirs:
                print(f"  mkdir -p {directory}")
        
        if missing_files:
            print("\nMissing Files:")
            for file in missing_files:
                print(f"  - {file}")
        
        if env_issues:
            print("\nEnvironment File Issues:")
            for issue in env_issues:
                print(f"  - {issue}")
        
        return False

def check_python_packages():
    """Check if required Python packages are installed."""
    required_packages = [
        'flask',
        'google.generativeai',
        'dotenv',
        'PIL',
        'werkzeug',
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.split('.')[0])
        except ImportError:
            missing_packages.append(package)
    
    if not missing_packages:
        print("\n✅ All required Python packages are installed!")
        return True
    else:
        print("\n❌ Some required Python packages are missing:")
        for package in missing_packages:
            if package == 'PIL':
                print(f"  - {package} (Install with: pip install pillow)")
            elif package == 'dotenv':
                print(f"  - {package} (Install with: pip install python-dotenv)")
            else:
                print(f"  - {package} (Install with: pip install {package})")
        
        print("\nRun this command to install all required packages:")
        print("  pip install -r dependencies.txt")
        return False

if __name__ == "__main__":
    print("=== Deepfake Detection Project Structure Verification ===\n")
    
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Checking project structure in: {current_dir}\n")
    
    structure_ok = check_structure()
    packages_ok = check_python_packages()
    
    if structure_ok and packages_ok:
        print("\n✅ Project structure verification complete! All checks passed.")
        print("\nRun the application with:")
        print("  python main.py")
        sys.exit(0)
    else:
        print("\n❌ Project structure verification failed! Please fix the issues above.")
        sys.exit(1)