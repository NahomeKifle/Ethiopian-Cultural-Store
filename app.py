from app import create_app
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = create_app()

if __name__ == "__main__":
    # Get port from environment variable or default to 5000
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)