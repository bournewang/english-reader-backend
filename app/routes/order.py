from flask import Blueprint, request, jsonify
import requests
import json
from dotenv import load_dotenv
import os
from flask_jwt_extended import jwt_required, get_jwt_identity

order_bp = Blueprint('order', __name__)

# Load environment variables from .env file
load_dotenv()

# Get PayPal credentials from environment variables
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
PAYPAL_SECRET = os.getenv('PAYPAL_SECRET')

# PayPal API URLs for the sandbox environment
PAYPAL_OAUTH_URL = "https://api.sandbox.paypal.com/v1/oauth2/token"
PAYPAL_ORDER_URL = "https://api.sandbox.paypal.com/v2/checkout/orders"

# Get PayPal Access Token
def get_paypal_token():
    response = requests.post(PAYPAL_OAUTH_URL, headers={
        "Accept": "application/json",
        "Accept-Language": "en_US"
    }, auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET), data={
        "grant_type": "client_credentials"
    })
    return response.json()['access_token']

@order_bp.route('/create', methods=['POST'])
@jwt_required()
def create_order():
    try:
        token = get_paypal_token()
        user_id = get_jwt_identity()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        data = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "description": "VIP Subscription",
                "amount": {
                    "currency_code": "USD",
                    "value": "10.00"  # Example amount
                }
            }]
        }
        response = requests.post(PAYPAL_ORDER_URL, headers=headers, json=data)
        return jsonify(response.json())
    except Exception as e:
        return jsonify(error=str(e)), 500

@order_bp.route('/capture/<order_id>', methods=['POST'])
@jwt_required()
def capture_order(order_id):
    try:
        token = get_paypal_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        capture_url = f"{PAYPAL_ORDER_URL}/{order_id}/capture"
        response = requests.post(capture_url, headers=headers)
        return jsonify(response.json())
    except Exception as e:
        return jsonify(error=str(e)), 500

@order_bp.route('/webhook', methods=['POST'])
def webhook():
    webhook_event = request.json
    # Verify the webhook event by sending it back to PayPal
    auth_algo = request.headers.get('PAYPAL-AUTH-ALGO')
    cert_url = request.headers.get('PAYPAL-CERT-URL')
    transmission_id = request.headers.get('PAYPAL-TRANSMISSION-ID')
    transmission_sig = request.headers.get('PAYPAL-TRANSMISSION-SIG')
    transmission_time = request.headers.get('PAYPAL-TRANSMISSION-TIME')

    # Verify the webhook event
    response = requests.post(
        'https://api.sandbox.paypal.com/v1/notifications/verify-webhook-signature',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {get_paypal_token()}'
        },
        json={
            'auth_algo': auth_algo,
            'cert_url': cert_url,
            'transmission_id': transmission_id,
            'transmission_sig': transmission_sig,
            'transmission_time': transmission_time,
            'webhook_id': os.getenv('PAYPAL_WEBHOOK_ID'),  # Your webhook ID from PayPal
            'webhook_event': webhook_event
        }
    )
    verification_status = response.json().get('verification_status')
    if verification_status == 'SUCCESS':
        # Handle the webhook event (e.g., update order status in your database)
        print("Webhook verified and event processed:", webhook_event)
        return jsonify(status='success'), 200
    else:
        return jsonify(status='error'), 400
