from flask import Blueprint, jsonify
from app.models.plan import Plan
from app.extensions import db

# Define a blueprint for the routes
plan_bp = Blueprint('plan', __name__)

@plan_bp.route('/list', methods=['GET'])
def get_plans():
    plans = Plan.query.all()
    plan_list = [{
        'product_id': plan.product_id,
        'plan_id': plan.plan_id,
        'name': plan.name,
        'description': plan.description,
        'interval_unit': plan.interval_unit,
        'interval_count': plan.interval_count,
        'value': plan.value,
        'currency': plan.currency
    } for plan in plans]
    
    return jsonify(plan_list)

# Ensure to register the blueprint in your app
