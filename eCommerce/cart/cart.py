from store.models import Product, Profile


class Cart():
    def __init__(self, request):
        self.session = request.session
        self.request = request
        # Get the cart from the session
        cart = self.session.get('session_key')
        # if the user is new, no session key will be found, so we create a new cart
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}
        
        # make the cart available to the class
        self.cart = cart
    
    def db_add(self, product, quantity):
        product_id = str(product)
        product_qty = str(quantity)
        if product_id not in self.cart:
            self.cart[product_id] = int(product_qty)
        else:
            pass
        self.session.modified = True

        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            current_user.update(old_cart=str(carty))

    def add(self, product, quantity):
        # add product to the cart
        product_id = str(product.id)
        product_qty = str(quantity)
        if product_id not in self.cart:
            self.cart[product_id] = int(product_qty)
        else:
            pass
        self.session.modified = True

        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            current_user.update(old_cart=str(carty))

    def __len__(self):
        return len(self.cart)
    
    def get_products(self):
        # get id from cart
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        return products
    
    def get_quantities(self):
        quantities = self.cart
        return quantities
    
    def update(self, product, quantity):
        '''updates the cart'''
        product_id = str(product)
        product_qty = int(quantity)
        our_cart = self.cart
        our_cart[product_id] = product_qty
        self.session.modified = True

        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            current_user.update(old_cart=str(carty))
        
        thing = self.cart
        return thing


    def delete(self, product):
        '''removes item from cart'''
        product_id = str(product)
        if product_id in self.cart:
            del self.cart[product_id]
            self.session.modified = True
        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            current_user.update(old_cart=str(carty))

    def get_total_price(self):
        '''get total price of items in cart'''
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        quantities = self.cart
        total_price = 0
        for key, value in quantities.items():
            for product in products:
                if product.id == int(key):
                    total_price += product.price * value
        return total_price