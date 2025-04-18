
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
import os
from django.conf import settings
from django.template import Context
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.template import Template

def add_to_cart_service(order,item,order_item):
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


def verify_signature(prev_signature,
        response_body_base64
    ) :
        """
        Verifies the signature of an eSewa response.
        """
        try:
            print("Start*")
            print(response_body_base64)
            response_body_json = base64.b64decode(response_body_base64).decode("utf-8")
            print(1*"*")
            response_data: dict[str, str] = json.loads(response_body_json)
            print(2*"*")
            received_signature: str = response_data["signature"]
            print(received_signature)
            print(3*"*")
            signed_field_names: str = response_data["signed_field_names"]
            field_names = signed_field_names.split(",")
            print(response_data)
            message: str = ",".join(
                f"{field_name}={response_data[field_name]}" for field_name in field_names
            )
            secret="8gBm/:&EnhH.1/q".encode('utf-8')
            message = message.encode('utf-8')
            hmac_sha256 = hmac.new(secret, message, hashlib.sha256)
            digest = hmac_sha256.digest()
            signature = base64.b64encode(digest).decode('utf-8')
            print(signature)
            is_valid: bool = received_signature == signature
            print(is_valid)
            return is_valid, response_data if is_valid else None
        except Exception as e:
            print(4*"*")
            print(f"Error verifying signature: {e}")
            return False, None


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


def handle_esewa_payment(total_amount, order):
    """
    Handles esewa payment process.
    """
    transaction_id=generate_transaction_uuid()
    signature_base64=generate_signature(total_amount=total_amount, transaction_uuid=transaction_id,key=config('ESEWA_SECRET_KEY'), product_code="EPAYTEST")
    order.signature=signature_base64
    order.save()
    return transaction_id, signature_base64


def get_esewa_status(data, dev: bool) -> str:
        """
        Fetches the transaction status from eSewa.
        """
  
        
        status_url_testing = f"https://rc.esewa.com.np/api/epay/transaction/status/?product_code={data["product_code"]}&total_amount={data["total_amount"]}&transaction_uuid={data["transaction_uuid"]}"
        status_url_prod = f"https://epay.esewa.com.np/api/epay/transaction/status/?product_code={data["product_code"]}&total_amount={data["total_amount"]}&transaction_uuid={data["transaction_uuid"]}"
        

        url = status_url_testing if dev else status_url_prod
        response = requests.get(url)

        if response.status_code != 200:
            raise requests.exceptions.RequestException(f"Error fetching status: {response.text}")

        response_data = response.json()
        return response_data.get("status", "UNKNOWN")

    
def SendNotificationEmail(user,payment,order_items,message,mail_subject):
    # Email Address Confirmation Email
        users = user
        from_email = settings.EMAIL_HOST_USER
        template_path = os.path.join(settings.BASE_DIR, "templates/emails/notification.html")
        email_subject = mail_subject
        context ={ 
            "message":message,
            "user":user,
            "payment":payment,
            "order_items":order_items,
        }
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        django_template = Template(html_content)
        rendered_html = django_template.render(Context(context))

        # Send the email
        msg = EmailMultiAlternatives(email_subject, "", from_email,[user.email])
        msg.attach_alternative(rendered_html, "text/html")
        msg.send()
        msg.failed_silently = True
        return True
    
 

def handle_order_complete(user,transaction_uuid, total_amount):
    """
    Handles order completion process for all payment methods.
    """
    order = Order.objects.get(user=user, ordered=False)
    payment = Payment()
    payment.pidx = transaction_uuid
    payment.user = user
    payment.amount =total_amount
    payment.status="COMPLETED"
    payment.save()
    order_items = order.items.all()
    order_items.update(ordered=True)
    for item in order_items:
            item.save()
    order.ordered = True
    order.payment = payment 
    order.ref_code = create_ref_code()
    order.save()
    mail_subject = "Order Confirmation"
    mail_message = f"Your order has been successfully placed. Your order ID is {order.ref_code}."
    SendNotificationEmail(user,payment,order_items,mail_message,mail_subject)
    
def handle_refund_request(form):
    """
    Handles refund request process.
    """
    ref_code = form.cleaned_data.get('ref_code')
    message = form.cleaned_data.get('message')
    email = form.cleaned_data.get('email')
    # edit the order
    try:
        order = Order.objects.get(ref_code=ref_code)
        order.refund_requested = True
        order.save  
        # store the refund
        refund = Refund()
        refund.order = order
        refund.reason = message
        refund.email = email
        refund.ref_code=ref_code
        refund.save()
        return True
    except ObjectDoesNotExist:
        return False
    
   