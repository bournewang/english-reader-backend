from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
import os
from dotenv import load_dotenv
from ..models.plan import Plan
from ..models.subscription import Subscription
from ..extensions import db
import uuid
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
BRAND_NAME = os.getenv('BRAND_NAME')
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

@paypal_bp.route('/plans', methods=['GET'])
@jwt_required()
def get_plans():
    plans = Plan.query.all()
    plan_list = [{
        'product_id': plan.product_id,
        'plan_id': plan.id,
        'name': plan.name,
        'description': plan.description,
        'interval_unit': plan.interval_unit,
        'interval_count': plan.interval_count,
        'value': plan.value,
        'currency': plan.currency
    } for plan in plans]
    
    return jsonify(plan_list)

@paypal_bp.route('/create-subscription', methods=['POST'])
@jwt_required()
def create_subscription():
    token = get_paypal_token()
    data = request.json
    user_id = get_jwt_identity()
    plan_id = data['plan_id']
    # fetch plan from database
    plan = Plan.query.get(plan_id)
    
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
                'brand_name': BRAND_NAME,
                'locale': 'en-US',
                'shipping_preference': 'NO_SHIPPING',
                'user_action': 'SUBSCRIBE_NOW',
                # 'return_url': f'https://api.englishreader.org/paypal/capture?subscription_id={subscription_id}',
                # 'cancel_url': 'http://localhost:3000/cancel'
            }
        }
    )
    logger.debug(f"request {PAYPAL_API_BASE}/v1/billing/subscriptions")
    logger.debug(response.json())
    response_data = response.json()
    if response.status_code == 201:
        subscription_id = response_data['id']
        approval_url = next(link['href'] for link in response_data['links'] if link['rel'] == 'approve')

        # Save the subscription to the database
        subscription = Subscription(
            id=subscription_id,
            user_id=user_id,
            plan_id=plan_id,
            plan_name=plan.name,
            status='PENDING'
        )
        db.session.add(subscription)
        db.session.commit()

        return jsonify({'subscription_id': subscription_id, 'approval_url': approval_url}), 201
    else:
        logger.error(f"Failed to create subscription: {response_data}")
        return jsonify({'error': response_data}), response.status_code

@paypal_bp.route('/subscriptions', methods=['GET'])
@jwt_required()
def get_subscriptions():
    user_id = get_jwt_identity()
    subscriptions = Subscription.query.filter_by(user_id=user_id).all()
    subscriptions_data = [subscription.info() for subscription in subscriptions]
    return jsonify(subscriptions=subscriptions_data), 200

@paypal_bp.route('/subscriptions/<string:subscription_id>/suspend', methods=['POST'])
@jwt_required()
def suspend_subscription(subscription_id):
    user_id = get_jwt_identity()
    subscription = Subscription.query.get(subscription_id)
    if not subscription:
        return jsonify({'error': 'Subscription not found'}), 404

    token = get_paypal_token()
    response = requests.post(
        f'{PAYPAL_API_BASE}/v1/billing/subscriptions/{subscription_id}/suspend',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        },
        json={'reason': 'User requested suspension'}
    )

    if response.status_code == 204:
        subscription.status = 'SUSPENDED'
        db.session.commit()

        subscriptions = Subscription.query.filter_by(user_id=user_id).all()
        subscriptions_data = [subscription.info() for subscription in subscriptions]        
        return jsonify(subscriptions=subscriptions_data), 200
    else:
        return jsonify({'error': 'Failed to suspend subscription'}), response.status_code

@paypal_bp.route('/subscriptions/<string:subscription_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_subscription(subscription_id):
    user_id = get_jwt_identity()
    subscription = Subscription.query.get(subscription_id)
    if not subscription:
        return jsonify({'error': 'Subscription not found'}), 404

    token = get_paypal_token()
    response = requests.post(
        f'{PAYPAL_API_BASE}/v1/billing/subscriptions/{subscription_id}/cancel',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        },
        json={'reason': 'User requested cancellation'}
    )

    if response.status_code == 204:
        subscription.status = 'CANCELLED'
        db.session.commit()
        
        subscriptions = Subscription.query.filter_by(user_id=user_id).all()
        subscriptions_data = [subscription.info() for subscription in subscriptions]        
        return jsonify(subscriptions=subscriptions_data), 200
    else:
        return jsonify({'error': 'Failed to cancel subscription'}), response.status_code

@paypal_bp.route('/subscriptions/<string:subscription_id>/activate', methods=['POST'])
@jwt_required()
def activate_subscription(subscription_id):
    user_id = get_jwt_identity()
    subscription = Subscription.query.get(subscription_id)
    if not subscription:
        return jsonify({'error': 'Subscription not found'}), 404

    token = get_paypal_token()
    response = requests.post(
        f'{PAYPAL_API_BASE}/v1/billing/subscriptions/{subscription_id}/activate',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        },
        json={'reason': 'User requested reactivation'}
    )

    if response.status_code == 204:
        subscription.status = 'ACTIVE'
        db.session.commit()
        
        subscriptions = Subscription.query.filter_by(user_id=user_id).all()
        subscriptions_data = [subscription.info() for subscription in subscriptions]        
        return jsonify(subscriptions=subscriptions_data), 200
    else:
        return jsonify({'error': 'Failed to activate subscription'}), response.status_code
        
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
    logger.debug(f"Webhook verification request: ")
    logger.debug(f'{PAYPAL_API_BASE}/v1/notifications/verify-webhook-signature')
    logger.debug({
            'Content-Type': 'application/json',
            'Authorization': f'Basic {PAYPAL_CLIENT_ID}:{PAYPAL_SECRET}'
        })
    logger.debug({
            'auth_algo': headers.get('Paypal-Auth-Algo'),
            'cert_url': headers.get('Paypal-Cert-Url'),
            'transmission_id': headers.get('Paypal-Transmission-Id'),
            'transmission_sig': headers.get('Paypal-Transmission-Sig'),
            'transmission_time': headers.get('Paypal-Transmission-Time'),
            'webhook_id': PAYPAL_WEBHOOK_ID,
            'webhook_event': body
        })
    logger.debug(f"Webhook verification response: {response.json()}")
    logger.debug(response.json())
    verification_status = response.json().get('verification_status')
    logger.debug(f"Verification status: {verification_status}")
    return verification_status == 'SUCCESS'


@paypal_bp.route('/webhook', methods=['POST'])
def webhook():
    try:
        headers = request.headers
        event_body = request.data.decode('utf-8')

        logger.info("Received webhook event")
        logger.debug(f"Headers: {headers}")
        logger.debug(f"Body: {event_body}")

        # Verify the webhook signature
        # if not verify_signature(event_body, headers):
        #     logger.warning("Invalid signature")
        #     return jsonify({'status': 'failure', 'message': 'Invalid signature'}), 400

        # Process the event
        event = request.json
        event_type = event['event_type']
        resource = event['resource']
        
        logger.info(f"Event type: {event_type}, Resource ID: {resource.get('id')}")

        if event_type == 'PAYMENT.SALE.COMPLETED':
            subscription_id = resource['billing_agreement_id']
            subscription = Subscription.query.get(subscription_id)
            if subscription:
                user = subscription.user
                user.premium = True
                plan = subscription.plan
                if subscription.user.expires_at and subscription.user.expires_at > datetime.utcnow():
                    current_expiry = subscription.user.expires_at
                else:
                    current_expiry = datetime.utcnow()                
                user.expires_at = calculate_new_expiry_date(current_expiry, plan.interval_unit, plan.interval_count)

                db.session.commit()
                logger.info(f"Updated user {user.id} premium status to {user.premium} and expires_at to {user.expires_at} due to payment completion")
                return jsonify({'status': 'success'}), 200

            logger.warning(f"Subscription {subscription_id} not found for payment completion")
            return jsonify({'status': 'failure', 'message': 'Subscription not found for payment completion'}), 404

        elif event_type.startswith('BILLING.SUBSCRIPTION'):
            subscription_id = resource.get('id')
            status = resource.get('status').upper()

            if not subscription_id:
                logger.warning("No subscription ID in the webhook event")
                return jsonify({'status': 'failure', 'message': 'No subscription ID in the event'}), 400

            # Log the event type and status
            logger.info(f"Event type: {event_type}, Subscription ID: {subscription_id}, Status: {status}")

            # Update subscription status but not user premium status
            subscription = Subscription.query.get(subscription_id)
            if subscription:
                subscription.status = status

                if status == 'EXPIRED':
                    user = subscription.user
                    user.premium = False
                    user.expires_at = None

                db.session.commit()

                logger.info(f"Updated subscription {subscription_id} status to {status}")
                return jsonify({'status': 'success'}), 200

            logger.warning(f"Subscription {subscription_id} not found")
            return jsonify({'status': 'failure', 'message': 'Subscription not found'}), 404

        logger.warning(f"Unhandled event type: {event_type}")
        return jsonify({'status': 'failure', 'message': 'Unhandled event type'}), 400
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({'status': 'failure', 'message': 'Internal server error'}), 500

@paypal_bp.route('/refund', methods=['POST'])
@jwt_required()
def process_refund():
    try:
        user_id = get_jwt_identity()
        subscription_id = request.json.get('subscription_id')
        
        subscription = Subscription.query.filter_by(user_id=user_id, subscription_id=subscription_id).first()
        if not subscription:
            return jsonify({'error': 'Subscription not found'}), 404

        # Process refund via PayPal API
        token = get_paypal_token()
        refund_url = f'{PAYPAL_API_BASE}/v1/payments/sale/{subscription_id}/refund'
        response = requests.post(
            refund_url,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            },
            json={'amount': {'total': str(subscription.plan_cost), 'currency': 'USD'}}
        )
        
        if response.status_code == 201:
            user = subscription.user
            user.premium = False
            user.expires_at = None
            db.session.commit()
            return jsonify({'status': 'success'}), 200
        else:
            return jsonify({'error': 'Failed to process refund'}), response.status_code
    except Exception as e:
        logger.error(f"Error processing refund: {e}")
        return jsonify({'status': 'failure', 'message': 'Internal server error'}), 500