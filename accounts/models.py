from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    ROLE_CUSTOMER = 'customer'
    ROLE_SELLER = 'seller'
    ROLE_CHOICES = [
        (ROLE_CUSTOMER, 'ลูกค้า / Customer'),
        (ROLE_SELLER, 'ผู้ขาย / Seller (Admin)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='เบอร์โทรศัพท์')
    bio = models.TextField(blank=True, null=True, verbose_name='เกี่ยวกับฉัน')
    created_at = models.DateTimeField(auto_now_add=True)

    def is_seller(self):
        return self.role == self.ROLE_SELLER or self.user.is_superuser

    def is_customer(self):
        return self.role == self.ROLE_CUSTOMER

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
        else:
            UserProfile.objects.create(user=instance)
