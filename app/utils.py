import hmac
import hashlib
import base64
from flask import request

def verify_webhook_signature(auth_algo, cert_url, transmission_id, timestamp, webhook_id, event_body, actual_signature, webhook_signature):
    expected_signature = hmac.new(webhook_signature.encode('utf-8'), (transmission_id + timestamp + webhook_id + event_body).encode('utf-8'), hashlib.sha256).digest()
    expected_signature = base64.b64encode(expected_signature).decode('utf-8')

    return hmac.compare_digest(expected_signature, actual_signature)
