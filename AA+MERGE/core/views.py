
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
from .services import add_to_cart_service

# Create your views here.
class HomeView(ListView):
    model = Item
    paginate_by = 8
    template_name = "home.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CATEGORY_CHOICES
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.GET.get('category')  
        search_query = self.request.GET.get('search') 
        if category:
            queryset = queryset.filter(category=category) 
        if search_query:  
            queryset = queryset.filter(title__icontains=search_query) 
        return queryset
    
class ItemDetailView(DetailView):
    model = Item
    template_name = "product_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = self.object
        average,full_stars, has_half_star = Review.get_average_rating(item)
        review_count = Review.get_review_count(item)
        context['avg_rating']=average
        context['full_stars']=full_stars
        context['has_half_star']=has_half_star
        context['review_count']=review_count
        context['reviews'] = item.reviews.filter(parent_review=None)  
        return context
    
    
    
@login_required
def add_to_cart(request,slug):
    item =get_object_or_404(Item,slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
        if add_to_cart_service(order,item,order_item):
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was added to your cart.")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:order-summary")
    
@login_required
def remove_from_cart(request,slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)



class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")
        
        
def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid




class CheckoutView(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()



            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True,

            }
            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                default=True
            )
            if shipping_address_qs.exists():
               context.update(
                    {'default_shipping_address': shipping_address_qs[0]})
            return render(self.request, "checkout.html", context)
        

        except Order.DoesNotExist:
            messages.error(self.request, "You do not have an active order.")
            return redirect("/")
        
        
    




    def post(self, *args, **kwargs):
        print(1*"*")
        form = CheckoutForm(self.request.POST or None)
        print(2*"*")
        
        try:
            print(3*"*")
            order = Order.objects.get(user=self.request.user, ordered=False)
            print("HEHE")
            if form.is_valid():
                print(4*"*")
                
                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print(5*"*")
                    
                    print("Using the defualt shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new shipping address")
                    print(6*"*")
                    
                    address = form.cleaned_data.get(
                        'address')
                    street_address = form.cleaned_data.get(
                        'street_address')
                    country = form.cleaned_data.get(
                        'country')
                    zip = form.cleaned_data.get('zip')
                    phone_number = form.cleaned_data.get('phone_number')

                    if is_valid_form([address, street_address, zip]):
                        existing_address = Address.objects.filter(user=self.request.user).first()
                        if existing_address:
                                # Update the existing address
                                existing_address.address = address
                                existing_address.street_address = street_address
                                existing_address.country = country
                                existing_address.zip = zip
                                existing_address.phone_number = phone_number
                                existing_address.save()  
                        else:
                                # Create a new address if one does not exist
                                shipping_address = Address(
                                    user=self.request.user,
                                    address=address,
                                    street_address=street_address,
                                    country=country,
                                    zip=zip,
                                    phone_number=phone_number
                                )
                                shipping_address.save()
                                order.shipping_address = shipping_address
                                order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")
                        return redirect("/checkout")

                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'E':
                    return redirect('core:payment', payment_option='esewa')
                elif payment_option == 'K':
                    return redirect('core:payment', payment_option='kalti')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")



def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except:
        messages.info(request, "This coupon does not exist")
        return redirect("core:checkout")

class AddCouponView(LoginRequiredMixin,View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')      
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout")
            except:
                return redirect("core:checkout")
        else:
            messages.info(self.request, "This coupon does not exist")
            return redirect("core:checkout")





# Generate transaction UUID
def generate_transaction_uuid():
    # Generate a simple transaction ID in the format shown in docs: xx-xxx-xx
    first = random.randint(10, 99)
    middle = random.randint(100, 999)
    last = random.randint(10, 99)
    return f"{first}-{middle}-{last}"



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


class PaymentView(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        order.ref_code = create_ref_code()
        total_amount = order.get_total()
        if kwargs['payment_option'] == 'esewa':
            transaction_id=generate_transaction_uuid()
            signature_base64=generate_signature(total_amount=total_amount, transaction_uuid=transaction_id,key=config('ESEWA_SECRET_KEY'), product_code="EPAYTEST")
            order.signature=signature_base64
            order.save()
            return render(self.request, "payment.html",context={
                'order':order,
                "method":"esewa",
                'uuid': transaction_id,
                "signature": signature_base64,})
            
        elif kwargs['payment_option'] == 'kalti':
            return render(self.request, "payment.html",context={'order':order,"method":"khalti"})
            
        else:
            messages.warning(self.request, "Invalid payment option selected")
            return redirect("core:checkout")

def init_khalti(request):
    url = "https://a.khalti.com/api/v2/epayment/initiate/"
    return_url = request.POST.get('return_url')
    website_url = request.POST.get('return_url')
    amount = request.POST.get('amount')
    purchase_order_id = request.POST.get('purchase_order_id')
    payload = json.dumps({
        "return_url": return_url,
        "website_url": website_url,
        "amount": amount,
        "purchase_order_id": purchase_order_id,
        "purchase_order_name": "test",
        "customer_info": {
        "name": "John Doe",
        "email": "test@khalti.com",
        "phone": "9800000001"
        }
    })

    # put your own live secet for admin
    headers = {
        'Authorization': f'key {config("KHALTI_API_KEY")}',
        'Content-Type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    new_res = json.loads(response.text)
    return redirect(new_res['payment_url'])


@login_required
def verify_khalti(request):
    url = "https://a.khalti.com/api/v2/epayment/lookup/"
    # if request.method == 'GET':
    #     headers = {
    #         'Authorization': f'key {config("KHALTI_API_KEY")}',
    #         'Content-Type': 'application/json',
    #     }
    #     pidx = request.GET.get('pidx')
    #     data = json.dumps({
    #         'pidx':pidx
    #     })
    #     res = requests.request('POST',url,headers=headers,data=data)
    #     new_res = json.loads(res.text)
        # if new_res['status'] == 'Completed':
    if True:
            order = Order.objects.get(user=request.user, ordered=False)
            payment = Payment()
            payment.pidx = "sdfhjPEZRWFJ5ygavzHWd5"
            payment.user = request.user
            payment.amount = int(order.get_total())
            payment.save()
            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                    item.save()
            order.ordered = True
            order.payment = payment 
            order.ref_code = create_ref_code()
            order.save()
            messages.success(request, "Your order was successful!")
            return redirect("/")
    else:
            messages.warning(request, "Payment not completed")
            return redirect("core:checkout")


def get_status(data, dev: bool) -> str:
        """
        Fetches the transaction status from eSewa.
        """
        print(data)
        print(data["product_code"])
  
        
        status_url_testing = f"https://rc.esewa.com.np/api/epay/transaction/status/?product_code={data["product_code"]}&total_amount={data["total_amount"]}&transaction_uuid={data["transaction_uuid"]}"
        status_url_prod = f"https://epay.esewa.com.np/api/epay/transaction/status/?product_code={data["product_code"]}&total_amount={data["total_amount"]}&transaction_uuid={data["transaction_uuid"]}"
        

        url = status_url_testing if dev else status_url_prod
        response = requests.get(url)

        if response.status_code != 200:
            raise requests.exceptions.RequestException(f"Error fetching status: {response.text}")

        response_data = response.json()
        print(response_data)
        return response_data.get("status", "UNKNOWN")

    

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
            print(3*"*")
            signed_field_names: str = response_data["signed_field_names"]
            field_names = signed_field_names.split(",")
            message: str = ",".join(
                f"{field_name}={response_data[field_name]}" for field_name in field_names
            )
            secret="8gBm/:&EnhH.1/q".encode('utf-8')
            message = message.encode('utf-8')
            hmac_sha256 = hmac.new(secret, message, hashlib.sha256)
            digest = hmac_sha256.digest()
            signature = base64.b64encode(digest).decode('utf-8')
            is_valid: bool = received_signature == signature
            print(is_valid)
            return is_valid, response_data if is_valid else None
        except Exception as e:
            print(4*"*")
            print(f"Error verifying signature: {e}")
            return False, None

@login_required
def verify_esewa(request):
    order = Order.objects.get(user=request.user, ordered=False)
    signature =order.signature
    is_valid, response_data = verify_signature(signature,
        response_body_base64 = request.GET.get("data"),
    )
    if is_valid:
        print(response_data)
        transaction_uuid=response_data["transaction_uuid"]
        order.signature=transaction_uuid
        order.save()
        if get_status(response_data,dev=True)== "COMPLETE":
           print("Payment is complete")
           messages.success(request, "Payment was successful!")
           order = Order.objects.get(user=request.user, ordered=False)
           payment = Payment()
           payment.pidx = transaction_uuid
           payment.user = request.user
           payment.amount =response_data["total_amount"]
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
           return redirect("core:home")
        else:
            # TODO:HAndle other requests
              messages.warning(request, "Payment not completed")
              return redirect("core:checkout")
    else:
        print("Signature verification failed")
        messages.warning(request, "Signature verification failed")
        return redirect("core:checkout")

        



class RequestRefundView(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        try:
            print("1")
            order = Order.objects.filter(user=self.request.user, ordered=True)
            
            context = {
                'orders': order,
                'form': form,
            }
            return render(self.request, "request_refund.html", context)

        except:
            print(2)
            messages.warning(self.request, "You do not have an previous order")
            return redirect("/")

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.ref_code=ref_code
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("core:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("core:request-refund")

@login_required
def submit_review(request, slug):
    item = get_object_or_404(Item, slug=slug)
    
    if request.method == 'POST':
        # Check if the form is for a reply or a review
        parent_review_id = request.POST.get('parent_review')
        message = request.POST.get('message')
        rating = request.POST.get('rating')

        if not message:
            messages.info(request, "Message and rating are required")
            return redirect(request.META.get('HTTP_REFERER', '/'))


        if parent_review_id:
            print("I m here")
            parent_review = get_object_or_404(Review, id=parent_review_id)
            # Create a reply to the review
            review = Review.objects.create(
                item=parent_review.item,  # Associate with the same item
                user=request.user,
                message=message,
                rating=parent_review.rating,  # Inherit rating from parent
                parent_review=parent_review,
            )
        else:
            # Create a new review
            review = Review.objects.create(
                item=item,
                user=request.user,
                message=message,
                rating=rating,
            )
            
        return redirect(request.META.get('HTTP_REFERER', '/'))

    
    

    template_name = "Testpayment.html"

    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(id=kwargs.get('order_id'))

                # Generate unique transaction ID
            transaction_uuid = generate_transaction_uuid()
                
                # Prepare payment data
            total_amount = str(order.get_total())
            product_code = "EPAYTEST"  # Use your actual product code in production
                
                # Create message string for signature
            message = (
                    f"total_amount={total_amount},"
                    f"transaction_uuid={transaction_uuid},"
                    f"product_code={product_code}"
                )
                
                # Generate signature using secret key
            signature = generate_signature(
                    config('ESEWA_SECRET_KEY'),
                    message
                )
                
                # Prepare payment data for template
            payment_data = {
                    'amount': total_amount,
                    'tax_amount': "0",
                    'product_service_charge': "0",
                    'product_delivery_charge': "0",
                    'total_amount': total_amount,
                    'transaction_uuid': transaction_uuid,
                    'product_code': product_code,
                    'signature': signature,
                    'success_url': request.build_absolute_uri(reverse('payment_success')),
                    'failure_url': request.build_absolute_uri(reverse('payment_failed')),
                }
                

                
            context = {
                    'order': order,
                    'payment_data': payment_data,
                    'method': 'esewa',
                }
                
            return render(request, TestPayment.html, context)
            
            return render(request, self.template_name, {'order': order})
            
        except Order.DoesNotExist:
            messages.error(request, "Order not found")
            return redirect('orders')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('orders')