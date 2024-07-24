from django.shortcuts import render

def home(request):
    return render(request=request, template_name='home.html')


def exam(request):
    return render(request=request, template_name='exam.html')

def contact_us(request):
    return render(request=request, template_name='contact-us.html')

def blog(request):
    return render(request=request, template_name='blog.html')


def payment(request):
    return render(request=request, template_name='payment.html')
