import firebase_admin
from firebase_admin import credentials, firestore, auth, storage  
import os

if not firebase_admin._apps:
    cred_path = os.path.join(os.getcwd(), 'firebase-auth.json')
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {'storageBucket': 'prjtest-53174.firebasestorage.app'})

firebase_auth = auth
firebase_db = firestore.client()
firebase_bucket = storage.bucket()
