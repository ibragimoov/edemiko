from flask import render_template, redirect, url_for, request
from models import User, Post
from flask_login import login_user, current_user, logout_user
from markdown import markdown

def register_routes(app, db, bcrypt):
    @app.route('/')
    def index():
        posts = Post.query.limit(10).all()

        for post in posts:
            post.content = markdown(post.content)

        return render_template('index.html', posts=posts)

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


    @app.route('/profile', methods=['GET'])
    def profile():
        return render_template('profile.html')