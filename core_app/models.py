from datetime import timedelta
import re

from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email=models.EmailField()
    first_name=models.CharField(max_length=256, null=False)
    last_name=models.CharField(max_length=256, null=False)
    phone_number = models.CharField(max_length=10, null=False, blank=False)
    is_editor=models.BooleanField(default=False)

    def __str__(self):
        return self.email
    
    @property
    def is_admin(self):
        """Return True if user is admin"""
        return self.is_superuser
    
    @property
    def is_editor(self):
        """Return True if user is editor"""
        return self.is_editor

class Subscription(models.Model):
    identifier=models.IntegerField()
    verbose=models.CharField(max_length=10)
    date_created=models.DateTimeField(auto_now_add=True)
    duration=models.PositiveIntegerField()

    def __str__(self):
        return self.verbose
    
    @property
    def is_subscription_valid(self):
        """Check if user is still able to work on tests"""
        return self.date_created < ( self.date_created + timedelta(hours=self.duration))
    

class Guest(models.Model):
    phone_number=models.CharField(max_length=10, null=False, blank=False)
    code=models.CharField(max_length=10, null=True)
    subscription=models.OneToOneField(Subscription, null=True, on_delete=models.SET_NULL)
    code_used_count=models.IntegerField(default=0)
    last_active=models.DateTimeField(null=True)
    date_created=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.phone_number
    
    @property
    def is_subscription_active(self):
        """Check if guest user subscription is active"""
        return self.subscription.is_subscription_valid()

    @property
    def is_code_expired(self):
        """Check if code is used atleast once"""
        try:
            sub = self.subscription.is_subscription_valid()
        except Exception:
            return False
        if not sub:
            self.code=None
            self.code_used_count=0
            self.subscription=None
            self.save()

            return True
        return False

    @property
    def is_code_valid(self):
        """Check if code entered by user is valid one"""
        code_length = len(self.code)
        pattern = r'AVI'
        found = re.findall(pattern=pattern, string=self.code)

        return (pattern in found) & (code_length == 10)
    
class Question(models.Model):
    question=models.CharField(max_length=256)
    correct_answer=models.CharField(max_length=256)
    dummy_answer_1=models.CharField(max_length=256)
    dummy_answer_2=models.CharField(max_length=256)
    dummy_answer_3=models.CharField(max_length=256)
    date_created=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question
    
    @property
    def get_random(self):
        """Return random questions"""
        queryset=self.objects.order_by('?')[:20]
        return queryset
    
    
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