from .views import (
    home, exam, contact_us, next_question, prev_question,
    blog, payment, generate_code, verify_code, reset_exam
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
    path('next-qt/', next_question, name="next_question"),
    path('prev-qt/', prev_question, name="prev_question"),
    path('reset/', reset_exam, name="reset_exam"),
]