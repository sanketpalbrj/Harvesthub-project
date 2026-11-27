from django.shortcuts import redirect


def cart_count(request):
    cart = request.session.get('cart', {})
    if isinstance(cart, dict):
        count = sum(cart.values())
    elif isinstance(cart, list):
        count = len(cart)
    else:
        count = 0
    return {'cart_count': count}

def addtocart(request, productid):
    cart = request.session.get('cart', {})
    productid = str(productid) # Session dictionary keys must be strings
    
    cart[productid] = cart.get(productid, 0) + 1
    request.session['cart'] = cart
    request.session.modified = True
    return redirect(request.META.get('HTTP_REFERER', '/')) # Or wherever you want to redirect