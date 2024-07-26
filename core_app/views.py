from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import CodeVerificationForm, GenerateCodeForm
from .models import Guest, Subscription, Payments


def home(request):
    form = GenerateCodeForm()
    return render(request=request, template_name='home.html', context={'form': form})


def exam(request):
    return render(request=request, template_name='exam.html')

def contact_us(request):
    return render(request=request, template_name='contact-us.html')

def blog(request):
    return render(request=request, template_name='blog.html')


def payment(request):
    return render(request=request, template_name='payment.html')


def simulate_payment():
    phone_number = '0729014388'
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
        user_sub = Subscription.objects.create(guest=user, identifier=1, verbose="week", duration=24)
        return user_sub
    user_sub.identifier=1
    user_sub.verbose="once"
    user_sub.duration=24
    user_sub.save()
    return user_sub

def generate_code(request):
    if request.method == 'POST':
        form = GenerateCodeForm(request.POST)
        if form.is_valid():
            # phone_number = form.cleaned_data['phone_number']
            # user, created = Guest.objects.get_or_create(phone_number=phone_number)
            # if not user:
            #     form.add_error("User not created")
            """payment simulation"""
            user = simulate_payment()
            user.generate_code()
            # After receiving phone number, initialize payment, code generation and code is sent
            # Redirect user to verify code page
            print(f"Sending code-> {user.code}")
            import time
            time.sleep(1)
            return JsonResponse({"status": "ok"})
        return redirect("core_app:home")


def verify_code(request):
    form = CodeVerificationForm()
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
            return redirect("core_app:exam")
        messages.error(request, "Injizamo kode neza")
        return redirect("core_app:verify_code")
    return render(request=request, template_name="verify_code.html", context={'form': form})
