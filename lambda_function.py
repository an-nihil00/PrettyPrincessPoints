import json

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

PUBLIC_KEY = "cba6e14c3d9a358497412181ec5c1497cdcca2d2af27747490c2e057e8370112" 
PING_PONG = {"type": 1}
RESPONSE_TYPES = {
        "PONG": 1,
        "ACK_NO_SOURCE": 2,
        "MESSAGE_NO_SOURCE": 3,
        "MESSAGE_WITH_SOURCE": 4,
        "ACK_WITH_SOURCE": 5
        }

def verify_signature(event):
    raw_body = event.get("rawBody")
    auth_sig = even["params"]["header"].get("x-signature-ed25519")
    auth_ts  = even["params"]["header"].get("x-signature-timestamp")

    message = auth_ts.encode() + raw_body.encode()
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    verify_key.verify(message, bytes.fromhex(auth_sig))

def ping_pong(body):
    return (body.get("type") == 1)

def lambda_handler(event, context):
    print(f"event {event}")
    try:
        verify_signature(event)
    except BadSignatureError as e:
        raise Exception(f"[UNAUTHORIZED] Invalid request signature: {e}")

    body = event.get("body-json")
    if ping_pong(body):
        return PING_PONG

    return {
            "type": RESPONSE_TYPES["MESSAGE_NO_SOURCE"],
            "data": {
                "tts":False,
                "content": "BEEP BOOP",
                "embeds": [],
                "allowed_mentions": []
            }
        }
    
