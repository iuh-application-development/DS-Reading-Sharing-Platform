import firebase_admin
from firebase_admin import credentials, firestore, auth
import os

if not firebase_admin._apps:
    cred_path = os.path.join(os.getcwd(), 'firebase-auth.json')
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

firebase_auth = auth
firebase_db = firestore.client()
