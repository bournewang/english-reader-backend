from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
import os
from dotenv import load_dotenv

paypal_bp = Blueprint('paypal', __name__)
load_dotenv()

PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
PAYPAL_SECRET = os.getenv('PAYPAL_SECRET')
PAYPAL_API_BASE = 'https://api-m.sandbox.paypal.com'  # Use sandbox for testing

# Simulated database
subscriptions = {}

def get_paypal_token():
    response = requests.post(
        f'{PAYPAL_API_BASE}/v1/oauth2/token',
        headers={'Accept': 'application/json'},
        auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET),
        data={'grant_type': 'client_credentials'}
    )
    return response.json()['access_token']

@paypal_bp.route('/create-product', methods=['POST'])
@jwt_required()
def create_product():
    token = get_paypal_token()
    data = request.json
    response = requests.post(
        f'{PAYPAL_API_BASE}/v1/catalogs/products',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        },
        json=data
    )
    return jsonify(response.json())

@paypal_bp.route('/create-plan', methods=['POST'])
@jwt_required()
def create_plan():
    token = get_paypal_token()
    data = request.json
    response = requests.post(
        f'{PAYPAL_API_BASE}/v1/billing/plans',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        },
        json=data
    )
    return jsonify(response.json())
