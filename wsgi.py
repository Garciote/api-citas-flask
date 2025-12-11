# wsgi.py
#!/usr/bin/env python3
import os
import sys

# For some reason we need to set the current directory to this otherwise dotenv doesn't work correctly.
sys.path.insert(0, os.path.dirname(__file__))

# Currently setting environment variable fallbacks here.
# They should be set by the .env file
os.environ.setdefault("MONGODB_URI", "")
os.environ.setdefault("JWT_SECRET_KEY", "")

# Load .env variables.
from dotenv import load_dotenv
load_dotenv(override=True)

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
