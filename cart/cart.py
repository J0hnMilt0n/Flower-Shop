from decimal import Decimal
from django.conf import settings
from shop.models import Product


class Cart:
    """Shopping cart implementation using sessions"""
    
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        """Add product to cart or update quantity"""
        product_id = str(product.id)
        
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.final_price)
            }
        
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        
        self.save()

    def remove(self, product):
        """Remove product from cart"""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        """Save cart to session"""
        self.session.modified = True

    def __iter__(self):
        """Iterate over cart items"""
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        
        for product in products:
            cart[str(product.id)]['product'] = product
        
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """Count total items in cart"""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """Calculate total cart price"""
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def get_discount(self, coupon=None):
        """Calculate discount if coupon applied"""
        if coupon:
            return (self.get_total_price() * coupon.discount) / 100
        return Decimal('0')

    def get_final_total(self, coupon=None):
        """Get final total after discount"""
        return self.get_total_price() - self.get_discount(coupon)

    def clear(self):
        """Clear the cart"""
        del self.session['cart']
        self.save()

    def get_item_count(self):
        """Get unique item count"""
        return len(self.cart)
