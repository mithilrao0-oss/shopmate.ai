import os
import tempfile

# Use a throw-away database. This must be set before the app is imported.
os.environ["SHOPMATE_DB"] = os.path.join(tempfile.mkdtemp(), "test.db")
