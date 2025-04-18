from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django_countries.fields import CountryField
from django.db.models import Avg, Count
from django.contrib.auth.models import AbstractUser


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
    ('primary', 'New'),
    ('secondary', 'Featured'),
    ('danger', 'Limited'),
    ('warning', 'Hot'),
    ('info', 'Exclusive'),
)



class CustomUser(AbstractUser):
    profile_pic = models.URLField(blank=True, null=True)
# Create your models here.
class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES,max_length=30, default='primary')
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField()
    Additional_information=models.CharField(max_length=100,null=True,blank=True)
    # stock=models.IntegerField(default=0)
    
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'slug': self.slug
        })
    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })
    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE,null=True)
    quantity = models.IntegerField(default=1)
    def __str__(self):
        return f"{self.quantity} of {self.item.title}"
    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    ref_code = models.CharField(max_length=20, blank=True, null=True)   
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    signature = models.CharField(max_length=256, blank=True, null=True)
    
    def __str__(self):
        return self.user.username

    def get_actual_total(self):
        total=0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total
        
    def get_total(self):
        total= self.get_actual_total()
        if  self.coupon:
            discount_per=self.coupon.percentage
            total = total - ((discount_per * total)/100)
        return total
    def get_coupon_amount(self):
        return self.get_actual_total()-self.get_total()
    
    
    
class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    address = models.CharField(max_length=100)
    street_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    phone_number=models.IntegerField()
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'
      
      

class Payment(models.Model):
    pidx = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Pending')

    def __str__(self):
        return self.user.username

        
class Coupon(models.Model):
    code = models.CharField(max_length=15)
    percentage = models.FloatField()


    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()
    ref_code=models.CharField(max_length=20)

    def __str__(self):
        return f"{self.pk}"


class Review(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    message = models.TextField()
    parent_review = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.rating} Stars'
    
    @classmethod
    def get_average_rating(cls, item):
        average = cls.objects.filter(item=item,parent_review__isnull=True).aggregate(Avg('rating'))['rating__avg']
        if average:
            average=round(average, 1)
            full_stars = int(average)  
            has_half_star = (average - full_stars) >= 0.1  
            return average,full_stars, has_half_star
        else:
            return 0,0, False

    @classmethod
    def get_review_count(cls, item):
        return cls.objects.filter(item=item,parent_review__isnull=True).count()
    

