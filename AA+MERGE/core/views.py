import base64
import hashlib
import hmac
import json
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView,DetailView,View
import requests
from .models import Item, Order, OrderItem,Address,Coupon,Payment
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from .forms import CheckoutForm,CouponForm
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



def genSha256(key, message):
    # Convert the key and message to bytes
    key = key.encode('utf-8')
    message = message.encode('utf-8')

    # Generate HMAC SHA256 digest
    hmac_sha256 = hmac.new(key, message, hashlib.sha256)
    digest = hmac_sha256.digest()

    # Convert digest to Base64-encoded string
    signature = base64.b64encode(digest).decode('utf-8')
    return signature

uid = str(uuid.uuid4())

class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()

            # Ensure the message format matches what the server expects
            message = "total_amount=100&transaction_uuid={{uid}}&product_code=EPAYTEST"

            # Generate the signature
            signature = genSha256("8gBm/:&EnhH.1/q", message)

            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True,
                'uuid': uid,
                "signature": signature,
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
            return redirect("order_summary")
    




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

class AddCouponView(View):
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


class PaymentView(View):
    def get(self, *args, **kwargs):
            url = "https://a.khalti.com/api/v2/epayment/initiate/"
            return_url = self.request.POST.get('return_url')
            website_url = self.request.POST.get('return_url')
            amount = self.request.POST.get('amount')
            purchase_order_id = self.request.POST.get('purchase_order_id')
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

def verifyKhalti(request):
    url = "https://a.khalti.com/api/v2/epayment/lookup/"
    if request.method == 'GET':
        headers = {
            'Authorization': f'key {config("KHALTI_API_KEY")}',
            'Content-Type': 'application/json',
        }
        pidx = request.GET.get('pidx')
        data = json.dumps({
            'pidx':pidx
        })
        res = requests.request('POST',url,headers=headers,data=data)
        new_res = json.loads(res.text)
        if new_res['status'] == 'Completed':
            order = Order.objects.get(user=request.user, ordered=False)
            payment = Payment()
            payment.pidx = pidx
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
            messages.success(request, "Your order was successful!")
            return redirect("/")
        else:
            messages.warning(request, "Payment not completed")
            return redirect("core:checkout")
        
        # else:
        #     # give user a proper error message
        #     raise BadRequest("sorry ")

        return redirect('/')
