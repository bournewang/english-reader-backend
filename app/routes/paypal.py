from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
import os
from dotenv import load_dotenv
from ..utils import verify_webhook_signature

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

@paypal_bp.route('/create-subscription', methods=['POST'])
@jwt_required()
def create_subscription():
    token = get_paypal_token()
    data = request.json
    user_id = get_jwt_identity()
    plan_id = data['plan_id']
    
    subscription_id = str(uuid.uuid4())
    subscriptions[subscription_id] = {'user_id': user_id, 'status': 'pending'}
    
    response = requests.post(
        f'{PAYPAL_API_BASE}/v1/billing/subscriptions',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        },
        json={
            'plan_id': plan_id,
            'application_context': {
                'brand_name': 'Your Brand',
                'locale': 'en-US',
                'shipping_preference': 'NO_SHIPPING',
                'user_action': 'SUBSCRIBE_NOW',
                'return_url': f'https://api.englishreader.org/paypal/capture?subscription_id={subscription_id}',
                'cancel_url': 'http://localhost:3000/cancel'
            }
        }
    )
    return jsonify(response.json())


@paypal_bp.route('/webhook', methods=['POST'])
def webhook():
    event = request.json
    transmission_id = request.headers.get('PayPal-Transmission-Id')
    timestamp = request.headers.get('PayPal-Transmission-Time')
    webhook_id = 'YOUR_WEBHOOK_ID'  # Replace with your webhook ID
    actual_signature = request.headers.get('PayPal-Transmission-Sig')
    webhook_signature = 'YOUR_WEBHOOK_SIGNATURE'  # Replace with your webhook signature
    cert_url = request.headers.get('PayPal-Cert-Url')
    auth_algo = request.headers.get('PayPal-Auth-Algo')

    event_body = request.data.decode('utf-8')

    if not verify_webhook_signature(auth_algo, cert_url, transmission_id, timestamp, webhook_id, event_body, actual_signature, webhook_signature):
        return jsonify({'status': 'failure', 'message': 'Invalid signature'}), 400

    # Handle the event
    if event['event_type'] == 'BILLING.SUBSCRIPTION.CREATED':
        subscription_id = event['resource']['id']
        # Handle the subscription creation event
    elif event['event_type'] == 'BILLING.SUBSCRIPTION.ACTIVATED':
        subscription_id = event['resource']['id']
        # Handle the subscription activation event
    elif event['event_type'] == 'BILLING.SUBSCRIPTION.CANCELLED':
        subscription_id = event['resource']['id']
        # Handle the subscription cancellation event
    # Handle other events...

    return jsonify({'status': 'success'}), 200
