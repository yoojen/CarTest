import json
from ast import literal_eval
import random

def generate_random_code()->str:
    """Return combined hex and immutable pattern random codes"""
    immutable_pattert = 'AVI' # To be stored in env
    random_number = random.randint(0, 9_999_999)
    return f"{immutable_pattert}{random_number}"

def transform_code_to_hex(code: str)->str:
    """Transform code to hex values"""
    code_hex_version = hex(code)
    return code_hex_version

def unpack_code(code: str)->str:
    """Return decoded str to match guest code"""
    immutable_pattert = 'AVI'  # To be stored in env
    code_portion = code[3:]
    code_to_integer = literal_eval(code_portion)
    return f"{immutable_pattert}{code_to_integer}"

def dump_dict(dict: dict):
    """Return json format of passed dictionary"""
    return json.dumps(dict)

# def create_guest_user(phone_number):
#     """Create guest user from phone number"""
#     user, created = Guest.objects.get_or_create(phone_number, last_active=datetime.now())
#     if created:
#         return user
#     else:
#         return None
    
def instantiate_api():
    pass

def process_payment():
    pass

def send_code():
    pass