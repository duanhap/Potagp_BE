import firebase_admin
from firebase_admin import auth, credentials
import os
import json
from flask import request, jsonify
from functools import wraps

# Helper function to initialize Firebase
def initialize_firebase():
    try:
        # Check if already initialized
        firebase_admin.get_app()
    except ValueError:
        # Not initialized, proceed to initialize
        cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY', 'firebase-service-account.json')
        cred_json = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')

        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("Firebase initialized from file.")
        elif cred_json:
            try:
                # Handle potential escaping issues in env vars
                cred_info = json.loads(cred_json)
                cred = credentials.Certificate(cred_info)
                firebase_admin.initialize_app(cred)
                print("Firebase initialized from environment variable.")
            except Exception as e:
                print(f"Error parsing FIREBASE_SERVICE_ACCOUNT_JSON: {e}")
        else:
            print("CRITICAL: Firebase not initialized. Missing service account key.")

# Initial call
initialize_firebase()

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
            # Double check initialization before verify
            initialize_firebase()
            # Verify the ID token
            decoded_token = auth.verify_id_token(token)
            request.user = decoded_token
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401
        
        return f(*args, **kwargs)
    
    return decorated
