import base64
import hashlib
import hmac
import json
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView,DetailView,View
import requests
from .models import Item, Order, OrderItem,Address,Coupon,Payment,Refund,CATEGORY_CHOICES
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from .forms import CheckoutForm,CouponForm,RefundForm
from django.shortcuts import redirect
import uuid
from decouple import config
import random
import string



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
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
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
    print("Im at AddCouponView")
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


def generate_signature(message, secret):
    """
    Generate HMAC SHA-256 signature in Base64 format.

    :param message: The message to be signed (string).
    :param secret: The secret key (string).
    :return: Base64 encoded signature (string).
    """
    # Convert message and secret to bytes
    message_bytes = message.encode('utf-8')
    secret_bytes = secret.encode('utf-8')

    # Create HMAC object using SHA-256
    hmac_obj = hmac.new(secret_bytes, message_bytes, hashlib.sha256)

    # Generate the HMAC signature (raw bytes)
    signature = hmac_obj.digest()

    # Encode the signature into Base64
    base64_signature = base64.b64encode(signature).decode('utf-8')

    return base64_signature



def generate_transaction_uuid():
    # Generate a random UUID
    full_uuid = uuid.uuid4()
    
    # Split the UUID into segments: first 2 digits, next 3 digits, and last 2 digits
    part1 = str(full_uuid).replace('-', '')[:2]  # First 2 digits
    part2 = str(full_uuid).replace('-', '')[2:5]  # Next 3 digits
    part3 = str(full_uuid).replace('-', '')[5:7]  # Last 2 digits
    
    # Format as '11-201-13' like pattern
    transaction_uuid = f"{part1}-{part2}-{part3}"

    return transaction_uuid

class PaymentView(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        
        if kwargs['payment_option'] == 'esewa':
            uuid=generate_transaction_uuid()
            # Ensure the message format matches what the server expects
            message = f"total_amount={order.get_total},transaction_uuid={uuid},product_code=EPAYTEST"

            # Generate the signature
            # signature = genSha256("8gBm/:&EnhH.1/q", message)
            signature = generate_signature(config('ESEWA_SECRET_KEY'), message)
            return render(self.request, "payment.html",context={
                'order':order,
                "method":"esewa",
                'uuid': uuid,
                "signature": signature,})
            
        elif kwargs['payment_option'] == 'kalti':
            return render(self.request, "payment.html",context={'order':order,"method":"khalti"})
            
        else:
            messages.warning(self.request, "Invalid payment option selected")
            return redirect("core:checkout")

def initkhalti(request):
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


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

@login_required
def verifyKhalti(request):
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

@login_required
def verifyEsewa(request):
    pass

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
