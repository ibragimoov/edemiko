from flask import render_template, redirect, url_for, request
from models import Product

def register_routes(app, db, bcrypt):
    @app.route('/')
    def index():
        all_products = Product.query.all()
        return render_template('index.html', products=all_products)

    cart_items = []
    @app.route('/cart')
    def cart():
        print(cart_items)

        return render_template('cart.html', cart_items=cart_items)


    @app.route('/cart_item/decrement/<int:id>', methods=['POST'])
    def decrement_cart_item(id):
        for cart_item in cart_items:
            if cart_item['id'] == id:
                if cart_item['count'] > 1:
                    cart_item['count'] -= 1

        return redirect(url_for('cart'))

    @app.route('/cart_item/increment/<int:id>', methods=['POST'])
    def increment_cart_item(id):
        for cart_item in cart_items:
            if cart_item['id'] == id:
                cart_item['count'] += 1

        print('после инкремента',cart_items)
        return redirect(url_for('cart'))

    @app.route('/add_to_cart', methods=['POST'])
    def add_to_cart():
        title = request.form['title']
        price = request.form['price']
        id = request.form['id']
        image_url = request.form['image_url']

        cart_items.append({
            "id": int(id),
            "title": title,
            "price": int(price),
            "image_url": image_url,
            "count": 1
        })

        return redirect(url_for('cart'))