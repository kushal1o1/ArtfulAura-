
import hmac
import hashlib
import base64
import json
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView,DetailView,View
import requests
from .models import Item, Order, OrderItem,Address,Coupon,Payment,Refund,CATEGORY_CHOICES,Review
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from .forms import CheckoutForm,CouponForm,RefundForm
from django.shortcuts import redirect
from django.urls import reverse
from decouple import config
import random
import string
import time

def add_to_cart_service(order,item,order_item,request):
    """
    Service to add an item to the cart.
    """
    if order.items.filter(item__slug=item.slug).exists():
        order_item.quantity += 1
        order_item.save()
        return True
    else:
        order.items.add(order_item)
        return False

def remove_from_cart_service(order,item,user):
    """
    Service to check if an order exists for the user.
    """
    if order.items.filter(item__slug=item.slug).exists():
        order_item = OrderItem.objects.filter(
                item=item,
                user=user,
                ordered=False
            )[0]
        order.items.remove(order_item)
        order_item.delete()
        return True
    else:
        return False
    
def remove_single_item_from_cart_service(order,item,user):
    """
    Service to remove a single item from the cart.
    """
    if order.items.filter(item__slug=item.slug).exists():
        order_item = OrderItem.objects.filter(
                item=item,
                user=user,
                ordered=False
            )[0]
        if order_item.quantity > 1:
            order_item.quantity -= 1
            order_item.save()
        else:
            order.items.remove(order_item)
            order_item.delete()
        return True
    else:
        return False