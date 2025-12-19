from django.db import models

# Create your models here.
from django.db import models

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"

    class Meta:
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_address = models.TextField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Order {self.id} - {self.product_name or 'No Product'}"
    
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200, unique=True)
    image = models.ImageField(upload_to='products/')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"