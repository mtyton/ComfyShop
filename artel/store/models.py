from django.db import models


class Product(models.Model):
    template = models.ForeignKey("exhibitions.Exhibit", on_delete=models.CASCADE)


class ProductSource(models.Model):
    name = models.CharField(max_length=255)


class ProductConfig(models.Model):
    source = models.ForeignKey(ProductSource, on_delete=models.CASCADE)
    color = models.CharField(max_length=255)
    
    price = models.FloatField()
