import os
class Config:
    SECRET_KEY = os.urandom(24)
    JSONIFY_PRETTYPRINT_REGULAR = True