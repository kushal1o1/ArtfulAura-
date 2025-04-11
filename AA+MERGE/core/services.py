

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

    