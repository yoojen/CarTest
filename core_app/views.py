from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from .forms import GenerateCodeForm
from .models import Guest


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

def generate_code(request):
    if request.method == 'POST':
        form = GenerateCodeForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            user, created = Guest.objects.get_or_create(phone_number=phone_number)
            if not user:
                form.add_error("User not created")
            user.generate_code()
            # After receiving phone number, initialize payment, code generation and code is sent
            # Redirect user to verify code page
            print(f"Sending code-> {user.code}")
            import time
            time.sleep(3)
            return JsonResponse({"status": "ok"})
        return redirect("core_app:home")


def verify_code(request):
    
    return render(request=request, template_name="verify_code.html")
