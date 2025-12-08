# wsgi.py
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
load_dotenv()

# From application(.py) import app (as _app)
from application import app as _app

# Validación de seguridad
if not os.getenv("MONGODB_URI"):
    print("ERROR: MONGODB_URI is not set")
    sys.exit(1)

if not os.getenv("JWT_SECRET_KEY"):
    print("ERROR: JWT_SECRET_KEY is not set")
    sys.exit(1)

# Set Apache's application to our app
application = _app