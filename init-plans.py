import requests
import os
from dotenv import load_dotenv
from app import create_app
from app.extensions import db
from app.models.plan import Plan

# Load environment variables from .env file
load_dotenv()

PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
PAYPAL_SECRET = os.getenv('PAYPAL_SECRET')
PAYPAL_API_BASE = 'https://api-m.sandbox.paypal.com'  # Use sandbox for testing

def get_paypal_token():
    response = requests.post(
        f'{PAYPAL_API_BASE}/v1/oauth2/token',
        headers={'Accept': 'application/json'},
        auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET),
        data={'grant_type': 'client_credentials'}
    )
    return response.json()['access_token']

def create_product():
    token = get_paypal_token()
    product_data = {
        "name": "VIP Membership",
        "description": "Subscription for VIP membership",
        "type": "SERVICE"
    }
    response = requests.post(
        f'{PAYPAL_API_BASE}/v1/catalogs/products',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        },
        json=product_data
    )
    print("create product response:")
    print(response.json())
    return response.json()

def create_plan(product_id, name, description, interval_unit, interval_count, value, currency):
    token = get_paypal_token()
    plan_data = {
        "product_id": product_id,
        "name": name,
        "description": description,
        "status": "ACTIVE",
        "billing_cycles": [
            {
                "frequency": {
                    "interval_unit": interval_unit,
                    "interval_count": interval_count
                },
                "tenure_type": "REGULAR",
                "sequence": 1,
                "total_cycles": 0,
                "pricing_scheme": {
                    "fixed_price": {
                        "value": value,
                        "currency_code": currency
                    }
                }
            }
        ],
        "payment_preferences": {
            "auto_bill_outstanding": True,
            "setup_fee_failure_action": "CANCEL",
            "payment_failure_threshold": 3
        }
    }
    response = requests.post(
        f'{PAYPAL_API_BASE}/v1/billing/plans',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        },
        json=plan_data
    )
    print("create plan response:")
    print(response.json())    
    return response.json()

def store_plan(product_id, plan_id, name, description, interval_unit, interval_count, value, currency):
    plan = Plan(
        product_id=product_id,
        plan_id=plan_id,
        name=name,
        description=description,
        interval_unit=interval_unit,
        interval_count=interval_count,
        value=value,
        currency=currency
    )
    db.session.add(plan)
    db.session.commit()

def main():
    app = create_app()
    app.app_context().push()
    
    # Create the product
    product_response = create_product()
    product_id = product_response['id']

    # Define plans
    plans = [
        {"name": "VIP Monthly Plan",    "description": "Monthly subscription for VIP membership",       "interval_unit": "MONTH", "interval_count": 1, "value": "9.90", "currency": "USD"},
        {"name": "VIP Quarterly Plan",  "description": "Quarterly subscription for VIP membership",     "interval_unit": "MONTH", "interval_count": 3, "value": "27.00", "currency": "USD"},
        {"name": "VIP Semi-Annual Plan","description": "Semi-Annual subscription for VIP membership",   "interval_unit": "MONTH", "interval_count": 6, "value": "48.00", "currency": "USD"},
        {"name": "VIP Annual Plan",     "description": "Annual subscription for VIP membership",        "interval_unit": "MONTH", "interval_count": 12, "value": "72.00", "currency": "USD"}
    ]

    # Create and store each plan
    for plan in plans:
        plan_response = create_plan(product_id, plan['name'], plan['description'], plan['interval_unit'], plan['interval_count'], plan['value'], plan['currency'])
        store_plan(product_id, plan_response['id'], plan['name'], plan['description'], plan['interval_unit'], plan['interval_count'], plan['value'], plan['currency'])
        print(f"Created plan: {plan['name']} with ID: {plan_response['id']}")

if __name__ == '__main__':
    main()
