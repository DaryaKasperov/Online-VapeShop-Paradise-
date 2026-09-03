from .models import CartItem


def cart(request):
    """Контекстный процессор для корзины"""
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    cart_items = CartItem.objects.filter(session_key=session_key)
    total_items = sum(item.quantity for item in cart_items)
    total_price = sum(item.get_total_price() for item in cart_items)

    return {
        'cart_items': cart_items,
        'cart_total_items': total_items,
        'cart_total_price': total_price,
    }