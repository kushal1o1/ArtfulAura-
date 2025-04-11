
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
    
# Generate transaction UUID
# def generate_transaction_uuid():
#     # Generate a simple transaction ID in the format shown in docs: xx-xxx-xx
#     first = random.randint(10, 99)
#     middle = random.randint(100, 999)
#     last = random.randint(10, 99)
#     return f"{first}-{middle}-{last}"


def generate_signature(
        total_amount: float, 
        transaction_uuid: str, 
        key: str = "8gBm/:&EnhH.1/q", 
        product_code: str = "EPAYTEST"
) -> str:
    """Generates hmac sha256 signature for eSewa payment gateway
    """
    if not total_amount or not transaction_uuid:
        raise ValueError("Both 'total_amount' and 'transaction_uuid' are required.")
    try:
        message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
        key = key.encode('utf-8')
        message = message.encode('utf-8')

        # Generate HMAC-SHA256 digest
        hmac_sha256 = hmac.new(key, message, hashlib.sha256)
        digest = hmac_sha256.digest()

        # Convert to Base64
        signature = base64.b64encode(digest).decode('utf-8')
        return signature
    except Exception as e:
        raise RuntimeError(f"Failed to generate signature: {e}")


def generate_transaction_uuid():
    current_time = int(time.time())
    first = random.randint(10, 99)
    middle = random.randint(100, 999)
    last = current_time % 100  
    return f"{first}-{middle}-{last}"

def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid

