"""
App settings.

Settings are read from environment variables so that secrets (like the JWT
secret key) never get hard-coded or pushed to GitHub. Copy `.env.example` to
`.env` and change the values for your own machine.
"""
import os

from dotenv import load_dotenv

# Load variables from a local `.env` file (if one exists) into os.environ.
load_dotenv()

# Where the database lives. SQLite stores everything in a single file,
# which is perfect for learning — no database server to install.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")

# Used to sign JWT tokens. Anyone who knows this can create valid tokens,
# so in a real deployment it must be long, random and kept secret.
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-key-change-me-in-production")

# The signing algorithm for JWTs. HS256 = HMAC with SHA-256.
ALGORITHM = "HS256"

# How long a login token stays valid.
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
