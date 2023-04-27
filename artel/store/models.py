from django.db import models


class ProductAuthor(models.Model):
    name = models.CharField(max_length=255)
    # TODO - author contact info? maybe foreignkey with user

class ProductTemplate(models.Model):
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    description = models.TextField()
    
    def get_images(self):
        return self.images.objects.all().values_list("image")


class ProductImage(models.Model):
    template = models.ForeignKey(
        ProductTemplate, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField()


class ProductConfig(models.Model):
    author = models.ForeignKey(ProductAuthor, on_delete=models.CASCADE)
    color = models.CharField(max_length=255)
    size = models.CharField(max_length=50)
    price = models.FloatField()


class Product(models.Model):
    template = models.ForeignKey(ProductTemplate, on_delete=models.CASCADE)
    config = models.ForeignKey(ProductConfig, on_delete=models.CASCADE)

