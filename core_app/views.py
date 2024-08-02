from django.utils import timezone
from datetime import timedelta
import random

from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect, render

from .utils import delete_session_infos, set_session_infos, check_guest_status, progress_setup, check_progress_presence
from .forms import CodeVerificationForm, GenerateCodeForm
from .models import Answers, Guest, InProgress, Subscription, Payments


def home(request):
    form = GenerateCodeForm()
    c_form = CodeVerificationForm()

    return render(request=request, template_name='home.html',
                  context={
                      'form': form,
                      'c_form': c_form
                      })


def exam(request):
    if not request.session.get('in_progress', None):
        messages.error(request, "Session has expired")
        return redirect("core_app:verify_code")
    current_index = request.session.get('current_index', None)
    user = request.session.get('guest', None)

    user=Guest.objects.filter(id=user).first()
    user_progress=InProgress.objects.filter(guest=user).first()
    if user_progress is None:
        messages.error(request=request, message="No progress")
        delete_session_infos(request)
        return redirect("core_app:verify_code")
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
                           'crt': request.session.get('crt'),
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
    verbose="once"
    duration=0
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
    user_sub.identifier=0
    user_sub.verbose="once"
    user_sub.duration=1
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
        guest = check_progress_presence(request=request)
        if guest:
            return redirect("core_app:exam")
    if request.method == 'POST':
        form = CodeVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            # Get guest
            guest_sub = check_guest_status(request=request, code=code)
            if guest_sub is None:
                messages.error(request, "Injizamo kode neza, Not valid")
                return redirect("core_app:verify_code")

            # Check if user already has an ongoing exam
            if request.session.get('in_progress', None):
                return redirect("core_app:exam")
            else:
                # Assign Questions
                progress = progress_setup(request=request, guest_sub=guest_sub)
                if progress is None:
                    messages.error(
                        request, "You're allowed to use one brwoser at time or reset your current exam if you've deleted your session manually")
                    return redirect("core_app:verify_code")
                progress.current_index = 0
                progress.save()
                # Mark code as used
                guest_sub.code_used_count += 1
                guest_sub.save()
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
            # Handle final screen redirection with appropriate argument
            guest_prog.ended_at = timezone.now()
            guest_prog.save()
            return redirect("core_app:final_screen")
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


def reset_exam(request):
    code = request.POST.get('code')
    guest_sub = check_guest_status(request=request, code=code)
    if guest_sub is not None:
        deleted = guest_sub.guest.in_progress.delete()
        if deleted:
            return JsonResponse({"status": "OK"})
    return JsonResponse({"status": "NOT_FOUND"})

def final_screen(request):
    user = request.session.get('guest', None)
    if user is None:
        messages.error(request=request, message="No session found")
        return redirect("core_app:verify_code")
    try:
        user = Guest.objects.filter(id=user).first()
        guest_prog = user.in_progress
        time_elapsed = str(guest_prog.ended_at - guest_prog.date_created)[2:7]
        guest_ans = guest_prog.answers
    except Guest.in_progress.RelatedObjectDoesNotExist as e:
        delete_session_infos(request)
        messages.error(request=request, message="You can not continue")
        return redirect("core_app:exam")
    count = 0
    final_report = []
    try:
        for q in guest_prog.questions.all():
            ans = q.answers.first()
            final_report.append({"idx": count + 1, "question": q.question, 
                                 "dummy_1": ans.dummy_answer_1, "dummy_2": ans.dummy_answer_2, 
                                 "dummy_3": ans.dummy_answer_3, "crt": ans.correct_answer, 
                                 "guest_resp": guest_ans[f'{count}'] if guest_ans[f'{count}'] else '-'})
            count = count + 1
        return render(request=request, template_name="final_screen.html",
                      context={'report': final_report,  "time_elapsed": time_elapsed,})
    except Exception as e:
        messages.error(request=request, message="Please answer all questions")
        return redirect("core_app:exam")
