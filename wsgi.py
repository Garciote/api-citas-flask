# wsgi.py
#!/usr/bin/env python3
import os
import sys

# For some reason we need to set the current directory to this otherwise dotenv doesn't work correctly.
sys.path.insert(0, os.path.dirname(__file__))

# Load .env variables.
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path, override=True)

# From application(.py) import app (as _app)
from application import app as _app

missing = []
if not os.getenv("MONGODB_URI"):
    missing.append("MONGODB_URI")
if not os.getenv("JWT_SECRET_KEY"):
    missing.append("JWT_SECRET_KEY")

if missing:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

# Set Apache's application to our app
application = _app
