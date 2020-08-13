import os
import firebase_admin
from os import getenv
from firebase_admin import credentials, firestore


bot_token = "1276054342:AAFnzpUenolykLvOns7CS1ItnuFsNOFiRvU"
# URL = os.environ.get('URL', 'https://julius-rock-bot.herokuapp.com/')
URL = os.environ.get('URL', 'https://134a7b7e7c8d.ngrok.io/')
port = int(os.environ.get('PORT', 8080))

pvt_key = getenv('private_key').replace('|', '\n').replace('\\=', '=')
credential_json = {
  "type": "service_account",
  "project_id": "virtualjulius-bot",
  "private_key_id": getenv('private_key_id'),
  "private_key": pvt_key,
  "client_email": getenv('client_email'),
  "client_id": getenv('client_id'),
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": getenv('client_x509_cert_url')
}

cred = credentials.Certificate(credential_json)
firebase_admin.initialize_app(cred)
db = firestore.client()
