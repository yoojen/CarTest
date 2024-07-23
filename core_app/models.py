from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone_number = models.CharField(max_length=10, null=False, blank=False)

class Subscription(models.Model):
    identifier=models.IntegerField()
    duration=models.DateTimeField(auto_now_add=True)
    verbose=models.CharField(max_length=10)

class Guest(models.Model):
    phone_number=models.CharField(max_length=10, null=False, blank=False)
    code=models.CharField(max_length=10, null=True)
    subscription=models.OneToOneField(Subscription, null=True, on_delete=models.SET_NULL)
    code_used_count=models.IntegerField(default=0)
    last_active=models.DateTimeField(null=True)
    date_created=models.DateTimeField(auto_now_add=True)

    def is_code_used(self):
        """Check if code is used atleast once"""
        pass

class Question(models.Model):
    question=models.CharField(max_length=256)
    correct_answer=models.CharField(max_length=256)
    dummy_answer_1=models.CharField(max_length=256)
    dummy_answer_2=models.CharField(max_length=256)
    dummy_answer_3=models.CharField(max_length=256)
    date_created=models.DateTimeField(auto_now_add=True)

class GuestPerformance(models.Model):
    question=models.ForeignKey(Question, on_delete=models.CASCADE)
    got_it_right=models.PositiveIntegerField()
    got_it_wrong=models.PositiveIntegerField()
    date_created=models.DateTimeField(auto_now_add=True)

class InProgress(models.Model):
    guest=models.OneToOneField(Guest, on_delete=models.CASCADE)
    questions=models.JSONField()
    is_done=models.BooleanField(default=False)
    date_created=models.DateTimeField(auto_now_add=True)

class History(models.Model):
    guest = models.ForeignKey(Guest, null=True, on_delete=models.SET_NULL)
    attempt_count=models.PositiveIntegerField()
    test_performance=models.JSONField()
    date_created=models.DateTimeField(auto_now_add=True)

PAYMENT_METHOD_CHOICES=(
    ("MTN", "MTN MoMo"), 
    ("AIRTEL", "Airtel Money")
)
class Payments(models.Model):
    guest=models.ForeignKey(Guest, null=True, on_delete=models.SET_NULL)
    method = models.CharField(max_length=256, choices=PAYMENT_METHOD_CHOICES)
    amount=models.CharField(max_length=256)
    subscription=models.ForeignKey(Subscription, null=True)

class Blog(models.Model):
    author=models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    title=models.CharField(max_length=1024)
    content=models.CharField(max_length=2024)
    date_created=models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    blog=models.ForeignKey(Blog, on_delete=models.CASCADE)
    contents=models.CharField(max_length=1024)
    guest_name=models.CharField(max_length=256)
    date_created=models.DateTimeField(auto_now_add=True)

class Reply(models.Model):
    parent_id=models.ForeignKey(Comment, on_delete=models.CASCADE)
    contents=models.CharField(max_length=1024)
    guest_name=models.CharField(max_length=256)
    date_created=models.DateTimeField(auto_now_add=True)

class LeaderBoard(models.Model):
    guest=models.OneToOneField(Guest, on_delete=models.CASCADE)
    scores=models.PositiveIntegerField(default=0)

    def get_position(self):
        """Return the current position of guest user"""
        pass