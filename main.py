import os
from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(dotenv_path):
    print(f"Loading environment from: {dotenv_path}")
    load_dotenv(dotenv_path)
else:
    print("Warning: .env file not found. Make sure to set up your environment variables!")

# Import the Flask app after loading environment variables
from app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
