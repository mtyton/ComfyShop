from django.db import models


class SiteConfiguration(models.Model):
    logo = models.ImageField(upload_to='images/icons', null=True, blank=True)
    shop_enabled = models.BooleanField(default=True)
    homepage = models.CharField(max_length=255, null=True, blank=True)

    NAVBAR_POSITION_CHOICES = [
        ('left', 'Left'),
        ('right', 'Right'),
    ]
    navbar_position = models.CharField(max_length=20, choices=NAVBAR_POSITION_CHOICES, default='left')
