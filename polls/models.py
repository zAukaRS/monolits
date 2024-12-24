from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.core.validators import FileExtensionValidator

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(
        upload_to='avatars/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        default='avatars/default.png'
    )
    bio = models.TextField(blank=True)
    nickname = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)

    def __str__(self):
        return self.user.username

class QuestionPost(models.Model):
    title = models.CharField(max_length=255)
    full_description = models.TextField()
    image = models.ImageField(upload_to='question_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    lifetime = models.DurationField(default=timedelta(days=7))
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    expires_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_active(self):
        return now() <= self.expires_at

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = now() + self.lifetime
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

@receiver(pre_save, sender=QuestionPost)
def set_expires_at(sender, instance, **kwargs):
    if not instance.expires_at:
        instance.expires_at = now() + instance.lifetime

class Option(models.Model):
    question = models.ForeignKey(QuestionPost, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    votes = models.IntegerField(default=0)
    voters = models.ManyToManyField(User, related_name='voted_options', blank=True)

    def __str__(self):
        return self.text

class UserVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(QuestionPost, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')


