from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.user import User
from ..extensions import db
import time

user_bp = Blueprint('user', __name__)

@user_bp.route('/locale', methods=['POST'])
@jwt_required()
def locale():
    data = request.get_json()
    user_id = get_jwt_identity()
    print("locale:")
    print(data['locale'])

    # update user's locale
    user = User.query.get(user_id)
    user.locale = data['locale']['locale']
    user.country = data['locale']['country']
    db.session.commit()

    return jsonify({"success": True, "data": user.info()})

