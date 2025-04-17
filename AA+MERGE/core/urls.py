
from django.contrib import admin
from django.urls import path
from . import views

from .views import(
    HomeView,ItemDetailView,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    OrderSummaryView,
    CheckoutView,
    AddCouponView,
    PaymentView,
    RequestRefundView,
    submit_review,
)

app_name='core'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('initiate/',views.init_khalti,name="initiate"),
    path('verify-khalti/',views.verify_khalti,name="verify-khalti"),
    path('verify-esewa/',views.verify_esewa,name="verify-esewa"),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),
    path('product/<slug>/submit_review/', submit_review, name='submit_review'),
    path("stripe_initiate/",views.initiate_stripe,name="stripe_initiate"),
    path("payment-sucess/",views.verify_stripe,name="sucess_page"),
    path("payment-cancel/",views.verify_stripe,name="sucess_page"),
    
    
    
]
