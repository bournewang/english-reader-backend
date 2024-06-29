from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

paypal_bp = Blueprint('paypal', __name__)
load_dotenv()

PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
PAYPAL_SECRET = os.getenv('PAYPAL_SECRET')
PAYPAL_API_BASE = 'https://api-m.sandbox.paypal.com'  # Use sandbox for testing
PAYPAL_WEBHOOK_ID = os.getenv('PAYPAL_WEBHOOK_ID')
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


def verify_webhook_signature(headers, body):
    response = requests.post(
        f'{PAYPAL_API_BASE}/v1/notifications/verify-webhook-signature',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Basic {PAYPAL_CLIENT_ID}:{PAYPAL_SECRET}'
        },
        json={
            'auth_algo': headers.get('Paypal-Auth-Algo'),
            'cert_url': headers.get('Paypal-Cert-Url'),
            'transmission_id': headers.get('Paypal-Transmission-Id'),
            'transmission_sig': headers.get('Paypal-Transmission-Sig'),
            'transmission_time': headers.get('Paypal-Transmission-Time'),
            'webhook_id': PAYPAL_WEBHOOK_ID,
            'webhook_event': body
        }
    )
    verification_status = response.json().get('verification_status')
    return verification_status == 'SUCCESS'


@paypal_bp.route('/webhook', methods=['POST'])
def webhook():
    try:
        headers = request.headers
        body = request.json

        logger.info("Received webhook event")
        logger.debug(f"Headers: {headers}")
        logger.debug(f"Body: {body}")

        # Verify the webhook signature
        if not verify_webhook_signature(headers, body):
            return jsonify({'status': 'failure', 'message': 'Invalid signature'}), 400

        # Process the event
        event_type = body['event_type']
        resource = body['resource']
        logger.info(f"Processing event: {event_type}")

        if event_type == 'BILLING.SUBSCRIPTION.CREATED':
            subscription_id = resource['id']
            # Handle subscription creation
            logger.info(f"Subscription created: {subscription_id}")
        elif event_type == 'BILLING.SUBSCRIPTION.ACTIVATED':
            subscription_id = resource['id']
            # Handle subscription activation
            logger.info(f"Subscription activated: {subscription_id}")
        elif event_type == 'BILLING.SUBSCRIPTION.CANCELLED':
            subscription_id = resource['id']
            # Handle subscription cancellation
            logger.info(f"Subscription cancelled: {subscription_id}")
        # Handle other events as needed

        return jsonify({'status': 'success'}), 200
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({'status': 'failure', 'message': 'Internal server error'}), 500