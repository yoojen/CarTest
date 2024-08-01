from django.utils import timezone
from datetime import timedelta
import random

from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect, render

from .utils import set_session_infos
from .forms import CodeVerificationForm, GenerateCodeForm
from .models import Answers, Guest, InProgress, Question, Subscription, Payments


def home(request):
    form = GenerateCodeForm()
    return render(request=request, template_name='home.html', context={'form': form})


def exam(request):
    if not request.session.get('in_progress', None):
        messages.error(request, "Session has expired")
        return redirect("core_app:verify_code")
    current_index = request.session.get('current_index', None)
    user = request.session.get('guest', None)
    user=Guest.objects.filter(id=user).first()
    user_progress=InProgress.objects.filter(guest=user).first()
    questions = user_progress.questions.order_by('id')
    qs_opts =Answers.objects.filter(
        question = questions[current_index]).first()
    q_opts = [qs_opts.dummy_answer_1, qs_opts.dummy_answer_2,
              qs_opts.dummy_answer_3, qs_opts.correct_answer]
    random.shuffle(q_opts)
    return render(request=request, template_name='exam.html', 
                  context={'index': current_index + 1, 
                           'question': questions[current_index],
                           'options': q_opts,
                           'crt': request.session.get('crt') # This will be used for next or back when user has initially answered id
                           })

def contact_us(request):
    return render(request=request, template_name='contact-us.html')

def blog(request):
    return render(request=request, template_name='blog.html')


def payment(request):
    form = GenerateCodeForm(request.POST)

    return render(request=request, template_name='payment.html', context={'form': form})


def simulate_payment():
    phone_number = '0729014388'
    verbose="day"
    duration=24
    user, created = Guest.objects.get_or_create(phone_number=phone_number)
    if not user:
        return None
    paid = Payments.objects.create(
        amount=1000, guest=user, method='MTN')
    if not paid:
        return None
    # User exists
    user_sub = Subscription.objects.filter(guest=user).first()
    if not user_sub:
        user_sub = Subscription.objects.create(guest=user, identifier=1, verbose=verbose, duration=duration)
        return user_sub
    user_sub.identifier=1
    user_sub.verbose="day"
    user_sub.duration=24
    user_sub.save()
    return user_sub

def generate_code(request):
    if request.method == 'POST':
        form = GenerateCodeForm(request.POST)
        if form.is_valid():
            """payment simulation"""
            user = simulate_payment()
            user.generate_code()
            print(f"Sending code-> {user.code}")
            import time
            time.sleep(1)
            return JsonResponse({"status": "ok"})
        return redirect("core_app:home")


def verify_code(request):
    form = CodeVerificationForm()
    if request.session.get('in_progress', None):
        return redirect("core_app:exam")
    if request.method == 'POST':
        form = CodeVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            # Get guest
            try:
                guest_sub = Subscription.objects.get(code=code)
                if not guest_sub.is_code_valid:
                    messages.error(request, "Injizamo kode neza, Not valid")
                    return redirect("core_app:verify_code")
                if guest_sub.is_code_expired:
                    messages.error(request, "No subscription")
                    return redirect("core_app:verify_code")

            except Exception as e:
                messages.error(request, "Injizamo kode neza")
                return redirect("core_app:verify_code")
            guest_sub.code_used_count += 1
            guest_sub.save()

            # Check if user already has an ongoing exam
            if request.session.get('in_progress', None):
                return redirect("core_app:exam")
            else:
                # Assign Questions
                progress = InProgress.objects.filter(guest=guest_sub.guest).first()
                if progress:
                    if progress.date_created + timedelta(minutes=20) > timezone.now():
                        messages.error(request, "You're allowed to use one brwoser at time or reset your current exam if you've deleted your session manually")
                        return redirect("core_app:verify_code")
                    # Remove in progress user items
                    progress.delete()
                assigned_questions = Question.objects.order_by('?')[:20]
                progress = InProgress.objects.create(guest=guest_sub.guest)
                progress.questions.set(assigned_questions)
                progress.current_index = 0
                progress.save()
                # Setting session
                set_session_infos(request=request, code=code, guest_sub=guest_sub, progress=progress)
            return redirect("core_app:exam")
        messages.error(request, "Injizamo kode neza")
        return redirect("core_app:verify_code")
    return render(request=request, template_name="verify_code.html", context={'form': form})


def next_question(request):
    if request.method=='POST':
        form = request.POST
        answer = form.get('answer', None)
        current_index=request.session.get('current_index', None)
        if current_index is None:
            messages.error(request, "Something wrong happened Or session has expired")
            return redirect("core_app:verify_code")
        user = request.session.get('guest', None)
        user = Guest.objects.filter(id=user).first()
        guest_prog = InProgress.objects.filter(guest=user).first()
        current_answers = guest_prog.answers
        if str(current_index) not in current_answers.keys():
            current_answers[current_index] = answer
            guest_prog.answers = current_answers
        else:
            if str(current_index + 1) in current_answers.keys():
                value = current_answers[f"{str(current_index+1)}"]
                request.session['crt']=value
            for k in current_answers.keys():
                if k == str(current_index):
                    current_answers[k]=answer
        guest_prog.save()

        if current_index == 19:
            # Handle final screen redirection with appropriate arguments
            print("No more, questions, final screen loading")
            return JsonResponse({})
        request.session['current_index'] = current_index + 1
    return redirect("core_app:exam")


def prev_question(request):
    current_index = request.session.get('current_index', None)
    if current_index is None:
        messages.error(request, "Something wrong happened Or session has exipired")
        return redirect("core_app:verify_code")
    user = request.session.get('guest', None)
    user = Guest.objects.filter(id=user).first()
    guest_prog = InProgress.objects.filter(guest=user).first()
    current_answers = guest_prog.answers
    if str(current_index - 1) in current_answers.keys():
        value = current_answers[f"{str(current_index-1)}"]
        request.session['crt'] = value
    guest_prog.save()

    if current_index == 0:
        return redirect("core_app:exam")
    request.session['current_index'] = current_index - 1
    return redirect("core_app:exam")

def check_guest_status(request, code):
    try:
        guest_sub = Subscription.objects.get(code=code)
        if not guest_sub.is_code_valid:
            return None
        if guest_sub.is_code_expired:
            return None
        return guest_sub
    except Exception as e:
        return None

def reset_exam(request):
    code = request.POST.get('code')
    guest_sub = check_guest_status(request=request, code=code)
    if guest_sub is not None:
        deleted = guest_sub.guest.in_progress.delete()
        if deleted:
            return JsonResponse({"status": "OK"})
    return JsonResponse({"status": "NOT_FOUND"})

def final_screen(request):
    return render(request, "final_screen.html")