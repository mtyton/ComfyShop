from django.db import models


class NavbarPosition(models.TextChoices):
    TOP = "top"
    LEFT = "left"
    RIGHT = "right"


class ComfyConfig(models.Model):
    logo = models.ImageField(upload_to="images")
    navbar_position = models.CharField(max_length=20, choices=NavbarPosition.choices, default=NavbarPosition.TOP)
    shop_enabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"Comfy Config - updated: {self.updated}"
