
import json
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView,DetailView,View
import requests
from .models import Item, Order, OrderItem,Address,Coupon,Payment,Refund,CATEGORY_CHOICES,Review,LABEL_CHOICES
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from .forms import CheckoutForm,CouponForm,RefundForm,ProfileUpdateForm
from django.shortcuts import redirect
from django.urls import reverse
from decouple import config
from .services import add_to_cart_service,remove_from_cart_service,remove_single_item_from_cart_service,generate_transaction_uuid,generate_signature,create_ref_code,is_valid_form,handle_esewa_payment,get_esewa_status,handle_order_complete,handle_refund_request,verify_signature
import stripe
from django.http import JsonResponse

stripe.api_key=config("STRIPE_API_KEY")

# import jsonify
# Create your views here.
class HomeView(ListView):
    model = Item
    paginate_by = 8
    template_name = "home.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CATEGORY_CHOICES
        context["labels"] = LABEL_CHOICES
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.GET.get('category') 
        label = self.request.GET.get('label') 
        search_query = self.request.GET.get('search') 
        if category:
            queryset = queryset.filter(category=category) 
        if label:
            queryset = queryset.filter(label=label)
        if search_query:  
            queryset = queryset.filter(title__icontains=search_query) 
        return queryset.order_by('?')
    
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
        # # check if the order item is in the order
        # if order.items.filter(item__slug=item.slug).exists():
        #     order_item.quantity += 1
        #     order_item.save()
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
        if remove_from_cart_service(order,item,request.user):
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
        if remove_single_item_from_cart_service(order,item,request.user):
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
                "payment_choices": form.payment_choices_with_images,

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
                elif payment_option == "S":
                    return redirect('core:payment', payment_option='stripe')
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


class PaymentView(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        order.ref_code = create_ref_code()
        total_amount = order.get_total()
        if kwargs['payment_option'] == 'esewa':
            transaction_id, signature_base64 = handle_esewa_payment(total_amount,order)
            return render(self.request, "payment.html",context={
                'order':order,
                "method":"esewa",
                'uuid': transaction_id,
                "signature": signature_base64,})
            
        elif kwargs['payment_option'] == 'kalti':
            return render(self.request, "payment.html",context={'order':order,"method":"khalti"})
        
        elif kwargs["payment_option"]=="stripe":
            return render(self.request, "payment.html",context={'order':order,"method":"stripe"})
            
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
        if get_esewa_status(response_data,dev=True)== "COMPLETE":
           print("Payment is complete")
           messages.success(request, "Payment was successful!")
           total_amount = response_data["total_amount"]
           handle_order_complete(request.user,transaction_uuid,total_amount)
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
            if handle_refund_request(form):
                messages.info(self.request, "Your request was received.")
                return redirect("core:request-refund")
            else:
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
            messages.info(request, "Replied to review")
            review = Review.objects.create(
                item=parent_review.item,  # Associate with the same item
                user=request.user,
                message=message,
                rating=parent_review.rating,  # Inherit rating from parent
                parent_review=parent_review,
            )
        else:
            # Create a new review
            messages.info(request, "Created a review")
            review = Review.objects.create(
                item=item,
                user=request.user,
                message=message,
                rating=rating,
            )
            
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
def calculate_order_amount(items):
    # Replace this constant with a calculation of the order's amount
    # Calculate the order total on the server to prevent
    # people from directly manipulating the amount on the client
    print("items",items)
    print(items)
    return int(items*100)
    
def initiate_stripe(request):
    order = Order.objects.get(user=request.user, ordered=False)
    try:
        # print("inside try")
        data = json.loads(request.body)
        # print("Received data:", data)
        # print("inside getting data")
        # Create a PaymentIntent with the order amount and currency

        intent = stripe.PaymentIntent.create(
            amount=calculate_order_amount(data['items']),
            currency='usd',
            # In the latest version of the API, specifying the `automatic_payment_methods` parameter is optional because Stripe enables its functionality by default.
            automatic_payment_methods={
                'enabled': True,
            },
        )
        return JsonResponse({
            'clientSecret': intent['client_secret']
        })
    except Exception as e:
        print("inside except")
        messages.info(request, f"An error occurred while creating the payment intent.{e}")
        print("Error:", e)
        return JsonResponse({'error': str(e)})

    # from django.http import JsonResponse
    # return JsonResponse({'clientSecret': session.client_secret})
    
def verify_stripe(request):
    """
    Verifies Stripe payment after redirect from success URL.
    Query params: payment_intent, payment_intent_client_secret, redirect_status
    """
    try:
        payment_intent_id = request.GET.get("payment_intent")
        client_secret = request.GET.get("payment_intent_client_secret")
        redirect_status = request.GET.get("redirect_status")

        if not payment_intent_id or not client_secret:
            return JsonResponse({"error": "Missing required parameters"}, status=400)

        # Retrieve payment from Stripe
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        if payment_intent.status != "succeeded":
            messages.info(request,"Sorry Payment was not sucessfull .Please try again")
            return redirect("core:checkout")
        if payment_intent.status == "succeeded":
            # Payment was successful, handle the order completion
            handle_order_complete(request.user, payment_intent.id, payment_intent.amount)
            messages.success(request, "Your order was successful!")
            return redirect("/")
        # Optional: log or process the payment
        return JsonResponse({
            "message": "Payment verified successfully",
            "payment_intent": {
                "id": payment_intent.id,
                "status": payment_intent.status,
                "amount": payment_intent.amount,
                "currency": payment_intent.currency,
                "redirect_status": redirect_status
            }
        })

    except stripe.error.StripeError as e:
        return JsonResponse({"error": f"Stripe error: {str(e)}"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)



@login_required
def profile_view(request):
    user = request.user
    default_address = Address.objects.filter(user=request.user).first()

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("core:profile_view")
    else:
        form = ProfileUpdateForm(instance=user)

    return render(request, 'profile.html', {
        'profile_form': form,
        'default_address': default_address,
    })
