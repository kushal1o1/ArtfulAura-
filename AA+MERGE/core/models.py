from django.conf import settings
from django.db import models
from django.shortcuts import reverse

CATEGORY_CHOICES = (
    ('P', 'Painting'),
    ('S', 'Sculpture'),
    ('DP', 'Digital Prints'),
    ('PH', 'Photography'),
    ('C', 'Crafts'),
    ('M', 'Mixed Media'),
    ('J', 'Jewelry'),
    ('T', 'Textiles'),
)


LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)
# Create your models here.
class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField()

    def __str__(self):
        return self.title



class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    def __str__(self):
        return self.title

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    def __str__(self):
        return self.title              