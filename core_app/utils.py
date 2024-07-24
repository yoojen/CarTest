import json
from ast import literal_eval
import random

def generate_random_code()->str:
    """Return combined hex and immutable pattern random codes"""
    immutable_pattert = 'AVI' # To be stored in env
    random = random.randint(0, 9_999_999)
    return f"{immutable_pattert}{random}"

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