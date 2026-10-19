def cart_count(request):
    """
    Context processor to provide total items in the shopping cart across all templates
    """
    cart = request.session.get('cart', [])
    return {'cart_count': len(cart)}
