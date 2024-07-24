from django.contrib.auth.models import UserManager

class UserCustomerManager(UserManager):
    def create_user(self, email, password, phone_number, **extra_fields):
        if not email:
            raise ValueError("Email is required to create user")
        if not phone_number:
            raise ValueError("You should add phone number")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, phone_number, **extra_fields):
        if not email:
            raise ValueError("Email is required to create user")
        if not phone_number:
            raise ValueError("You should add phone number")
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)
