from .views import (
        home, exam, contact_us,
    blog, payment, generate_code, verify_code
    )
from django.urls import path


urlpatterns=[
    path('home/', home, name='home'),
    path('exam/', exam, name='exam'),
    path('contact_us/', contact_us, name='contact_us'),
    path('blog/', blog, name='blog'),
    path('payment/', payment, name='payment'),
    path('gen-code/', generate_code, name="generate_code"),
    path('continue/', verify_code, name="verify_code"),

]