import json

from flask import render_template, redirect, url_for, request
from models import Product, User, Order, OrderByProduct
from flask_login import login_user, current_user, logout_user

def calc_cart(cart_items):
    totalPrice = 0
    totalCount = 0
    for cart_item in cart_items:
        totalPrice += cart_item['price'] * cart_item['count']
        totalCount += cart_item['count']

    totalPrice = '{:,.2f}'.format(totalPrice)

    return { "totalPrice": totalPrice, "totalCount": totalCount }

def register_routes(app, db, bcrypt):
    @app.route('/')
    def index():
        all_products = Product.query.limit(4).all()
        tshirts = Product.query.filter(Product.category_id == 2).limit(4).all()
        return render_template('index.html', popular_products=all_products, tshirts=tshirts)

    cart_items = []
    @app.route('/cart')
    def cart():
        totalInfo = calc_cart(cart_items)
        return render_template('cart.html', cart_items=cart_items, totalPrice=totalInfo['totalPrice'], totalCount=totalInfo['totalCount'])


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

        return redirect(url_for('cart'))

    @app.route('/add_to_cart', methods=['POST'])
    def add_to_cart():
        title = request.form['title']
        price = request.form['price']
        id = request.form['id']
        image_url = request.form['image_url']
        count = request.form['count']

        for item in cart_items:
            if item['id'] == int(id):
                item['count'] += int(count)
                return redirect(url_for('cart'))

        cart_items.append({
            "id": int(id),
            "title": title,
            "price": int(price),
            "image_url": image_url,
            "count": int(count)
        })

        return redirect(url_for('cart'))

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'GET':
            return render_template('signup.html')
        elif request.method == 'POST':
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            password = request.form['password']
            repassword = request.form['re-password']

            if password != repassword:
                return render_template('signup.html', error='Пароли не совпадают')

            user = User.query.filter(User.email == email).first()

            if not user:
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

                new_user = User(first_name=first_name, last_name=last_name, email=email, password=hashed_password)

                db.session.add(new_user)
                db.session.commit()

                return redirect(url_for('signin'))
            else:
                return render_template('signup.html', error=f'пользователь {email} уже есть')

    @app.route('/signin', methods=['GET', 'POST'])
    def signin():
        if request.method == 'GET':
            return render_template('signin.html')
        elif request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            user = User.query.filter(User.email == email).first()
            if not user:
                return render_template('signin.html', error=f'пользователь не найден')

            if bcrypt.check_password_hash(user.password, password):
                # Допиши логику авторизации
                login_user(user)
                return redirect(url_for('index'))
            else:
                return render_template('signin.html', error=f'неправильная почта или пароль')


    @app.route('/logout', methods=['POST'])
    def logout():
        logout_user()
        return redirect(url_for('index'))


    @app.route('/checkout', methods=['POST'])
    def checkout():
        if not current_user.is_authenticated:
            return redirect(url_for('signin'))
        else:
            totalInfo = calc_cart(cart_items)
            return render_template('checkout.html', cart_items=cart_items, totalPrice=totalInfo['totalPrice'], totalCount=totalInfo['totalCount'])


    @app.route('/order-success')
    def order_success():
        order_id = request.args['order_id']
        address = request.args['address']

        return render_template('order_success.html', order_id=order_id, address=address)

    @app.route('/order', methods=['POST'])
    def order():
        total = request.form['total']
        address = request.form['address']
        post_code = request.form['post_code']
        products_from_req = request.form['products']
        products = json.loads(products_from_req)

        # создание заказа в бд
        order = Order(total=total, address=address, post_code=post_code, user_id=current_user.id)
        db.session.add(order)
        db.session.commit()

        # создание товаров в заказе
        for product in products:
            order_product = OrderByProduct(order_id=order.id, product_id=product['id'], count=product['count'])
            db.session.add(order_product)

        db.session.commit()

        return redirect(url_for('order_success', order_id=order.id, address=address))


    @app.route('/profile')
    def profile():
        orders = Order.query.filter(Order.user_id == current_user.id).all()

        return render_template('profile.html', orders=orders)


    @app.route('/order/<int:id>')
    def order_details(id):
        order = Order.query.get(id)

        if not order:
            return redirect(url_for('index'))

        products_in_order = OrderByProduct.query.filter(OrderByProduct.order_id == order.id).all()

        return render_template('order_details.html', order=order, products_in_order=products_in_order)


    @app.route('/product/<int:id>')
    def product(id):
        product_info = Product.query.get(id)

        if not product_info:
            return redirect(url_for('index'))

        similar_products = Product.query.filter(Product.category_id == product_info.category_id, Product.id != id).all()

        return render_template('product.html', product=product_info, similar_products=similar_products)


    @app.route('/search', methods=['GET'])
    def search():
        search_query = request.args['query']

        products = Product.query.filter(Product.title.ilike(f'%{search_query}%')).all()

        if len(products) == 0:
            other_products = Product.query.limit(4).all()
        else:
            other_products = []

        return render_template('search.html', search_query=search_query, products=products, other_products=other_products)