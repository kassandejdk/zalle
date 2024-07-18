import random
import string
import os
from django.db import models
from django.contrib.auth.models import User

from django.conf import settings


def renommer_image(instance, nom_fichier):
    upload_to = 'image/'
    extention = nom_fichier.split('.')[-1]
    if instance.user.username:
        nom_fichier = "photo_profile/{}.{}".format(instance.user.username, extention)
    return os.path.join(upload_to, nom_fichier)

class Level(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True)
    type_profile = models.CharField(max_length=30, blank=True)
    verification_code = models.CharField(max_length=6, blank=True)
    is_verified = models.BooleanField(default=False)

    
    eleve = 'eleve'
    enseignant = 'enseignant'
    parent = 'parent'

    type_user = [
        (eleve, 'eleve'),
        (enseignant, 'enseignant'),
        (parent, 'parent')
    ]

    type_profile = models.CharField(max_length=100, choices=type_user, default=eleve)

    def __str__(self):
        return self.user.username
class OTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.code}"
    


###################################"
class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transID = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    token = models.CharField(max_length=255)

    

    def __str__(self):
        return f"Transaction {self.transID} - {self.status}"
    

class Subscription(models.Model):
    STANDARD = 'standard'
    PREMIUM = 'premium'

    SUBSCRIPTION_CHOICES = [
        (STANDARD, 'Standard'),
        (PREMIUM, 'Premium'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription_type = models.CharField(max_length=10, choices=SUBSCRIPTION_CHOICES, default=STANDARD)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.subscription_type}"
