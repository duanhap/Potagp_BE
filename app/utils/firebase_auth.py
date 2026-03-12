import firebase_admin
from firebase_admin import auth, credentials
import os
import json
from flask import request, jsonify
from functools import wraps

# Initialize Firebase Admin SDK
cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY', 'firebase-service-account.json')
cred_json = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')

if os.path.exists(cred_path):
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
elif cred_json:
    try:
        cred_info = json.loads(cred_json)
        cred = credentials.Certificate(cred_info)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Error initializing Firebase from environment variable: {e}")
else:
    print(f"Warning: Firebase service account key not found at {cred_path} and FIREBASE_SERVICE_ACCOUNT_JSON env var is missing.")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            # Verify the ID token while checking if the token is revoked by passing check_revoked=True.
            decoded_token = auth.verify_id_token(token)
            request.user = decoded_token  # Contains uid, email, etc.
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401
        
        return f(*args, **kwargs)
    
    return decorated
