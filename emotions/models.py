from django.db import models
from django.contrib.auth.models import Permission, User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
from django.shortcuts import reverse
from PIL import Image
from django.utils.text import slugify

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=True, null=True)
    avatar = models.ImageField(upload_to='media/profile', blank=True, null=True)
    email = models.EmailField(null=True, unique=True)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.get_or_create(user=instance)
            
    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, created, **kwargs):
        if created:
            instance.profile.save()
            
    def __str__(self):
        return self.user.username

class Emotion(models.Model):
    kid = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)  # Record capture time
    face_emotion = models.CharField(max_length=30, null=True)
    voice_emotions = models.CharField(max_length=30, null=True)
    probability = models.IntegerField(null=True, blank=True, default=2)

    def __str__(self):
        return f'{self.face_emotion} {self.probability}'

class Pose(models.Model):
    kid = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)  # Record capture time
    pose = models.CharField(max_length=30, null=True)
    pose_data = models.TextField()  # Store pose data as JSON or any other suitable format
    probability = models.IntegerField(null=True, blank=True, default=2)


    def __str__(self):
        return f'{self.kid.username} {self.timestamp}'
    

class Plans(models.Model):
    plan_name = models.CharField(max_length=100, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=10, null=True)
    desc = models.TextField(null=True)
    slug = models.SlugField(unique=True, max_length=100, null=True)

    def __str__(self):
        return self.plan_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.plan_name)
        super().save(*args, **kwargs)

class PaymentHistory(models.Model):
    PENDING = "P"
    COMPLETED = "C"
    FAILED = "F"

    STATUS_CHOICES = (
        (PENDING, ("pending")),
        (COMPLETED, ("completed")),
        (FAILED, ("failed")),
    )

    email = models.EmailField(unique=True)
    plan = models.ForeignKey(Plans, on_delete=models.CASCADE)
    payment_status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default=PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.name

class EmailHist(models.Model):
     timestamp = models.DateTimeField(auto_now_add=True)
     title = models.CharField(max_length=100, null=True)


     def __str__(self):
         return self.title