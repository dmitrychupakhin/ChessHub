from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_delete, pre_save
from django.contrib.auth.models import AbstractUser
import os

class User(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    balance = models.IntegerField(default=0)
    
    
# Сигнал для удаления изображения при удалении пользователя
@receiver(post_delete, sender=User)
def auto_delete_profile_picture_on_delete(sender, instance, **kwargs):
    if instance.profile_picture:
        if os.path.isfile(instance.profile_picture.path):
            os.remove(instance.profile_picture.path)

# Сигнал для удаления старого изображения при обновлении фотографии пользователя
@receiver(pre_save, sender=User)
def auto_delete_profile_picture_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False
    try:
        old_picture = User.objects.get(pk=instance.pk).profile_picture
    except User.DoesNotExist:
        return False

    new_picture = instance.profile_picture
    if not old_picture == new_picture:
        if os.path.isfile(old_picture.path):
            os.remove(old_picture.path)
