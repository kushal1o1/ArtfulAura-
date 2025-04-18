from django.contrib import admin
from django.utils.html import format_html
from .models import Item, OrderItem, Order,Payment,Coupon,Address,Refund,Review, CustomUser
from django.contrib.auth.admin import UserAdmin


admin.site.register(CustomUser, UserAdmin)

def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'being_delivered',
                    'received',
                    'refund_requested',
                    'refund_granted',
                    'shipping_address',
                    'payment',
                    'coupon'
                    ]
    list_display_links = [
        'user',
        'shipping_address',
        'payment',
        'coupon'
    ]
    list_filter = ['ordered',
                   'being_delivered',
                   'received',
                   'refund_requested',
                   'refund_granted']
    search_fields = [
        'user__username',
        'ref_code'
    ]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'address',
        'street_address',
        'country',
        'zip',
        'phone_number',
        'default',
        
    ]
    list_filter = ['default', 'country']
    search_fields = ['user', 'street_address', 'address', 'zip']

class ItemAdmin(admin.ModelAdmin):
    list_display = ('image_tag','title', 'price', 'discount_price', 'category', 'label', 'slug', 'Additional_information')
    readonly_fields = ['image_tag']  
    writable_fields = ['label']  # Make image field writable in the admin panel
    list_filter = ('category', 'label')  # Filter items by category and label

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto;" />'.format(obj.image.url))
        return "No Image"

    image_tag.short_description = 'Image'

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'ordered', 'quantity')
    list_filter = ('ordered', 'user')  #  to filter orders by user or ordered status
    search_fields = ('user__username', 'item__title')
    
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('pidx', 'user', 'amount', 'timestamp')
    list_filter = ('user', 'timestamp')  # Filter payments by user or date
    search_fields = ('pidx', 'user__username')  # Enable search by payment ID and user username
    readonly_fields = ('timestamp',)


class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'percentage')  # Display coupon code and percentage in the list view
    search_fields = ('code',)  # Enable search by coupon code
    list_filter = ('percentage',)
    
class RefundAdmin(admin.ModelAdmin):
    list_display = ('order', 'ref_code', 'email', 'accepted')  # Display key fields in the list view
    list_filter = ('accepted', 'order')  # Add filters for accepted status and order
    search_fields = ('ref_code', 'email', 'order__id')  # Enable search by ref_code, email, and order ID
    list_editable = ('accepted',)  # Make the 'accepted' field editable directly in the list view
    
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('item', 'user', 'rating', 'message', 'parent_review', 'created_at')  # Display review fields
    list_filter = ('rating', 'item', 'user')  # Filter reviews by rating, item, or user
    search_fields = ('user__username', 'item__title', 'message')  # Search reviews by username, item title, or message
    readonly_fields = ('created_at',)  # Make the 'created_at' field read-only
    list_editable = ('rating',)
    
admin.site.register(Item,ItemAdmin)
admin.site.register(OrderItem,OrderItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment,PaymentAdmin)
admin.site.register(Coupon,CouponAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Refund,RefundAdmin)
admin.site.register(Review,ReviewAdmin)


