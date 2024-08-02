import json
from ast import literal_eval
import random
from datetime import timedelta

# Django packages
from django.utils import timezone

def generate_random_code()->str:
    """Return combined hex and immutable pattern random codes"""
    immutable_pattert = 'AVI' # To be stored in env
    random_number = random.randint(1_000_000, 9_999_999)
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


def set_session_infos(request, code, guest_sub, progress):
    """Setting exam session"""
    print("setting session.......")
    request.session['code'] = code
    request.session['guest'] = guest_sub.guest.id
    request.session['current_index'] = progress.current_index
    request.session['in_progress'] = True

def delete_session_infos(request):
    """Setting exam session"""
    print("setting session.......")
    request.session.pop('guest')
    request.session.pop('current_index')
    request.session.pop('in_progress')
    request.session.pop('code')
    request.session.modified=True

# def create_guest_user(phone_number):
#     """Create guest user from phone number"""
#     user, created = Guest.objects.get_or_create(phone_number, last_active=datetime.now())
#     if created:
#         return user
#     else:
#         return None


def check_guest_status(request, code):
    from core_app.models import Subscription
    try:
        guest_sub = Subscription.objects.get(code=code)
        if not guest_sub.is_code_valid:
            return None
        if guest_sub.is_code_expired:
            return None
        return guest_sub
    except Exception as e:
        return None
    

def progress_setup(request, guest_sub):
    from .models import InProgress, Question
    progress = InProgress.objects.filter(guest=guest_sub.guest).first()
    if progress:
        if progress.date_created + timedelta(minutes=20) > timezone.now():
            return None
        # Remove in progress user items
        progress.delete()
    assigned_questions = Question.objects.order_by('?')[:20]
    progress = InProgress.objects.create(guest=guest_sub.guest)
    progress.questions.set(assigned_questions)
    return progress

def check_progress_presence(request):
    from .models import InProgress, Guest
    user = request.session['guest']
    try:
        guest = Guest.objects.filter(pk=user)
        progress = InProgress.objects.filter(guest=guest).first()
    except ValueError:
        return None
    return guest

def instantiate_api():
    pass

def process_payment():
    pass

def send_code():
    pass