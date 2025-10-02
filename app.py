from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    avatar_url = db.Column(db.String(200), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    orders = db.relationship('Order', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(200))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    reviews = db.relationship('Review', backref='product', lazy=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    shipping_address = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Newsletter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    preferences = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    tags = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def index():
    featured_products = Product.query.limit(8).all()
    categories = Category.query.all()
    return render_template('index.html', featured_products=featured_products, categories=categories)

@app.route('/products')
def products():
    category_id = request.args.get('category')
    search = request.args.get('search', '')
    
    query = Product.query
    if category_id:
        query = query.filter_by(category_id=category_id)
    if search:
        query = query.filter(Product.name.contains(search))
    
    products = query.all()
    categories = Category.query.all()
    return render_template('products.html', products=products, categories=categories, search=search)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    reviews = Review.query.filter_by(product_id=product_id).all()
    return render_template('product_detail.html', product=product, reviews=reviews)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form.get('full_name', '')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'error')
            return render_template('register.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            full_name=full_name
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if not session.get('user_id'):
        flash('Please login first!', 'error')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    user.full_name = request.form.get('full_name', user.full_name)
    user.bio = request.form.get('bio', user.bio)
    user.avatar_url = request.form.get('avatar_url', user.avatar_url)
    
    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/cart')
def cart():
    if not session.get('user_id'):
        flash('Please login first!', 'error')
        return redirect(url_for('login'))
    
    cart_items = session.get('cart', [])
    products = []
    total = 0
    
    for item in cart_items:
        product = Product.query.get(item['product_id'])
        if product:
            products.append({
                'product': product,
                'quantity': item['quantity']
            })
            total += product.price * item['quantity']
    
    return render_template('cart.html', products=products, total=total)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if not session.get('user_id'):
        return jsonify({'error': 'Please login first!'})
    
    product_id = int(request.form['product_id'])
    quantity = int(request.form['quantity'])
    
    if 'cart' not in session:
        session['cart'] = []
    
    cart = session['cart']
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += quantity
            break
    else:
        cart.append({'product_id': product_id, 'quantity': quantity})
    
    session['cart'] = cart
    return jsonify({'success': 'Product added to cart!'})

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if not session.get('user_id'):
        flash('Please login first!', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        shipping_address = request.form['shipping_address']
        notes = request.form.get('notes', '')
        
        cart_items = session.get('cart', [])
        if not cart_items:
            flash('Your cart is empty!', 'error')
            return redirect(url_for('cart'))
        
        total = 0
        for item in cart_items:
            product = Product.query.get(item['product_id'])
            total += product.price * item['quantity']
        
        order = Order(
            user_id=session['user_id'],
            total_amount=total,
            shipping_address=shipping_address,
            notes=notes
        )
        db.session.add(order)
        db.session.flush()
        
        for item in cart_items:
            product = Product.query.get(item['product_id'])
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                price=product.price
            )
            db.session.add(order_item)
        
        db.session.commit()
        session['cart'] = []
        flash('Order placed successfully!', 'success')
        return redirect(url_for('orders'))
    
    cart_items = session.get('cart', [])
    products = []
    total = 0
    
    for item in cart_items:
        product = Product.query.get(item['product_id'])
        if product:
            products.append({
                'product': product,
                'quantity': item['quantity']
            })
            total += product.price * item['quantity']
    
    return render_template('checkout.html', products=products, total=total)

@app.route('/orders')
def orders():
    if not session.get('user_id'):
        flash('Please login first!', 'error')
        return redirect(url_for('login'))
    
    user_orders = Order.query.filter_by(user_id=session['user_id']).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=user_orders)

@app.route('/add_review', methods=['POST'])
def add_review():
    if not session.get('user_id'):
        return jsonify({'error': 'Please login first!'})
    
    product_id = int(request.form['product_id'])
    rating = int(request.form['rating'])
    comment = request.form.get('comment', '')
    
    review = Review(
        user_id=session['user_id'],
        product_id=product_id,
        rating=rating,
        comment=comment
    )
    db.session.add(review)
    db.session.commit()
    
    return jsonify({'success': 'Review added successfully!'})

@app.route('/newsletter', methods=['POST'])
def newsletter():
    email = request.form['email']
    name = request.form.get('name', '')
    preferences = request.form.get('preferences', '')
    
    if Newsletter.query.filter_by(email=email).first():
        flash('Email already subscribed!', 'error')
    else:
        subscriber = Newsletter(email=email, name=name, preferences=preferences)
        db.session.add(subscriber)
        db.session.commit()
        flash('Successfully subscribed to newsletter!', 'success')
    
    return redirect(url_for('index'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        
        contact_msg = Contact(name=name, email=email, subject=subject, message=message)
        db.session.add(contact_msg)
        db.session.commit()
        
        flash('Message sent successfully!', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/blog')
def blog():
    posts = Blog.query.order_by(Blog.created_at.desc()).all()
    return render_template('blog.html', posts=posts)

@app.route('/blog/<int:post_id>')
def blog_post(post_id):
    post = Blog.query.get_or_404(post_id)
    return render_template('blog_post.html', post=post)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = []
    
    if query:
        products = Product.query.filter(Product.name.contains(query)).all()
        posts = Blog.query.filter(Blog.title.contains(query)).all()
        results = {'products': products, 'posts': posts}
    
    return render_template('search.html', query=query, results=results)

# Search Results Display
@app.route('/search_results')
def search_results():
    query = request.args.get('q', '')
    return f"<h1>Search Results for: {query}</h1><p>No results found for your search.</p>"

# User Profile Lookup
@app.route('/user_profile')
def user_profile():
    user_id = request.args.get('id')
    if user_id:
        try:
            user = User.query.get(int(user_id))
            if user:
                return f"<h1>User Profile</h1><p>Username: {user.username}</p><p>Bio: {user.bio}</p>"
        except ValueError:
            return f"<h1>User Profile</h1><p>Searching for user: {user_id}</p><p>Invalid user ID format</p>"
    return "<h1>User not found</h1>"

# Product Review Display
@app.route('/review_display')
def review_display():
    review_id = request.args.get('id')
    if review_id:
        try:
            review = Review.query.get(int(review_id))
            if review:
                return f"<h1>Review</h1><p>Comment: {review.comment}</p>"
        except ValueError:
            return f"<h1>Review</h1><p>Searching for review: {review_id}</p><p>Invalid review ID format</p>"
    return "<h1>Review not found</h1>"

# Newsletter Subscriber Lookup
@app.route('/newsletter_preferences')
def newsletter_preferences():
    email = request.args.get('email')
    if email:
        subscriber = Newsletter.query.filter_by(email=email).first()
        if subscriber:
            return f"<h1>Newsletter Preferences</h1><p>Email: {subscriber.email}</p><p>Preferences: {subscriber.preferences}</p>"
        else:
            return f"<h1>Newsletter Preferences</h1><p>Searching for email: {email}</p><p>Subscriber not found</p>"
    return "<h1>Subscriber not found</h1>"

# Contact Message Display
@app.route('/contact_display')
def contact_display():
    contact_id = request.args.get('id')
    if contact_id:
        try:
            contact = Contact.query.get(int(contact_id))
            if contact:
                return f"<h1>Contact Message</h1><p>Subject: {contact.subject}</p><p>Message: {contact.message}</p>"
        except ValueError:
            return f"<h1>Contact Message</h1><p>Searching for contact: {contact_id}</p><p>Invalid contact ID format</p>"
    return "<h1>Contact message not found</h1>"

# Blog Post Content Display
@app.route('/blog_content')
def blog_content():
    post_id = request.args.get('id')
    if post_id:
        try:
            post = Blog.query.get(int(post_id))
            if post:
                return f"<h1>{post.title}</h1><p>Author: {post.author}</p><div>{post.content}</div>"
        except ValueError:
            return f"<h1>Blog Post</h1><p>Searching for post: {post_id}</p><p>Invalid post ID format</p>"
    return "<h1>Blog post not found</h1>"

# Order Notes Display
@app.route('/order_notes')
def order_notes():
    order_id = request.args.get('id')
    if order_id:
        try:
            order = Order.query.get(int(order_id))
            if order:
                return f"<h1>Order Notes</h1><p>Order ID: {order.id}</p><p>Notes: {order.notes}</p>"
        except ValueError:
            return f"<h1>Order Notes</h1><p>Searching for order: {order_id}</p><p>Invalid order ID format</p>"
    return "<h1>Order not found</h1>"

# Product Description Display
@app.route('/product_description')
def product_description():
    product_id = request.args.get('id')
    if product_id:
        try:
            product = Product.query.get(int(product_id))
            if product:
                return f"<h1>{product.name}</h1><p>Description: {product.description}</p>"
        except ValueError:
            return f"<h1>Product</h1><p>Searching for product: {product_id}</p><p>Invalid product ID format</p>"
    return "<h1>Product not found</h1>"

# Category Description Display
@app.route('/category_description')
def category_description():
    category_id = request.args.get('id')
    if category_id:
        try:
            category = Category.query.get(int(category_id))
            if category:
                return f"<h1>{category.name}</h1><p>Description: {category.description}</p>"
        except ValueError:
            return f"<h1>Category</h1><p>Searching for category: {category_id}</p><p>Invalid category ID format</p>"
    return "<h1>Category not found</h1>"

# User Information Display
@app.route('/user_name')
def user_name():
    user_id = request.args.get('id')
    if user_id:
        try:
            user = User.query.get(int(user_id))
            if user:
                return f"<h1>User Information</h1><p>Full Name: {user.full_name}</p><p>Username: {user.username}</p>"
        except ValueError:
            return f"<h1>User Information</h1><p>Searching for user: {user_id}</p><p>Invalid user ID format</p>"
    return "<h1>User not found</h1>"

# Admin Routes
@app.route('/admin')
def admin_dashboard():
    if not session.get('is_admin'):
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    stats = {
        'users': User.query.count(),
        'products': Product.query.count(),
        'orders': Order.query.count(),
        'reviews': Review.query.count()
    }
    
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, recent_orders=recent_orders)

@app.route('/admin/users')
def admin_users():
    if not session.get('is_admin'):
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/products')
def admin_products():
    if not session.get('is_admin'):
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    products = Product.query.all()
    categories = Category.query.all()
    return render_template('admin/products.html', products=products, categories=categories)

@app.route('/admin/orders')
def admin_orders():
    if not session.get('is_admin'):
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)

@app.route('/admin/reviews')
def admin_reviews():
    if not session.get('is_admin'):
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('admin/reviews.html', reviews=reviews)

@app.route('/admin/newsletter')
def admin_newsletter():
    if not session.get('is_admin'):
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    subscribers = Newsletter.query.order_by(Newsletter.created_at.desc()).all()
    return render_template('admin/newsletter.html', subscribers=subscribers)

@app.route('/admin/contacts')
def admin_contacts():
    if not session.get('is_admin'):
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    contacts = Contact.query.order_by(Contact.created_at.desc()).all()
    return render_template('admin/contacts.html', contacts=contacts)

@app.route('/admin/blog')
def admin_blog():
    if not session.get('is_admin'):
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    posts = Blog.query.order_by(Blog.created_at.desc()).all()
    return render_template('admin/blog.html', posts=posts)

@app.route('/admin/add_product', methods=['POST'])
def admin_add_product():
    if not session.get('is_admin'):
        return redirect(url_for('index'))
    
    name = request.form['name']
    description = request.form['description']
    price = float(request.form['price'])
    stock_quantity = int(request.form['stock_quantity'])
    category_id = int(request.form['category_id'])
    image_url = request.form.get('image_url', '')
    
    product = Product(
        name=name,
        description=description,
        price=price,
        stock_quantity=stock_quantity,
        category_id=category_id,
        image_url=image_url
    )
    db.session.add(product)
    db.session.commit()
    
    flash('Product added successfully!', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/add_category', methods=['POST'])
def admin_add_category():
    if not session.get('is_admin'):
        return redirect(url_for('index'))
    
    name = request.form['name']
    description = request.form.get('description', '')
    
    category = Category(name=name, description=description)
    db.session.add(category)
    db.session.commit()
    
    flash('Category added successfully!', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/add_blog_post', methods=['POST'])
def admin_add_blog_post():
    if not session.get('is_admin'):
        return redirect(url_for('index'))
    
    title = request.form['title']
    content = request.form['content']
    author = request.form['author']
    tags = request.form.get('tags', '')
    
    post = Blog(title=title, content=content, author=author, tags=tags)
    db.session.add(post)
    db.session.commit()
    
    flash('Blog post added successfully!', 'success')
    return redirect(url_for('admin_blog'))

@app.route('/admin/update_order_status', methods=['POST'])
def admin_update_order_status():
    if not session.get('is_admin'):
        return redirect(url_for('index'))
    
    order_id = int(request.form['order_id'])
    status = request.form['status']
    admin_notes = request.form.get('admin_notes', '')
    
    order = Order.query.get(order_id)
    if order:
        order.status = status
        if admin_notes:
            order.notes = admin_notes
        db.session.commit()
        flash('Order status updated successfully!', 'success')
    
    return redirect(url_for('admin_orders'))

# Initialize database
with app.app_context():
    db.create_all()
    
    # Create admin user if not exists
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@techstore.com',
            password_hash=generate_password_hash('admin123'),
            full_name='Administrator',
            bio='System administrator with full access to all features',
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
    
    # Create sample user for testing
    if not User.query.filter_by(username='testuser').first():
        test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('password123'),
            full_name='Test User',
            bio='Regular user for testing purposes'
        )
        db.session.add(test_user)
        db.session.commit()
    
    # Create sample categories
    if Category.query.count() == 0:
        categories = [
            Category(name='Electronics & Computers', description='Smartphones, laptops, tablets, headphones, smart home devices, and cutting-edge technology'),
            Category(name='Clothing, Shoes & Jewelry', description='Fashion for men, women, and kids. Shoes, accessories, watches, and jewelry from top brands'),
            Category(name='Books & Audible', description='Best-selling books, textbooks, e-books, audiobooks, and educational materials'),
            Category(name='Home & Kitchen', description='Furniture, home decor, kitchen appliances, tools, and garden supplies for your home')
        ]
        for category in categories:
            db.session.add(category)
        db.session.commit()
    
    # Create sample products
    if Product.query.count() == 0:
        products = [
            Product(name='Apple iPhone 15 Pro Max 256GB - Natural Titanium', description='The iPhone 15 Pro Max features a titanium design, A17 Pro chip, and advanced camera system with 5x optical zoom. Includes USB-C connectivity and Action Button for enhanced functionality.', price=1199.00, stock_quantity=47, category_id=1, image_url='https://m.media-amazon.com/images/I/81Os1SDWpcL._AC_SX679_.jpg'),
            Product(name='Samsung Galaxy S24 Ultra 512GB - Titanium Black', description='Samsung Galaxy S24 Ultra with S Pen, 200MP camera, and AI-powered features. Features a 6.8-inch Dynamic AMOLED 2X display and titanium construction.', price=1299.99, stock_quantity=23, category_id=1, image_url='https://m.media-amazon.com/images/I/71w3e1oKiNL._AC_SX679_.jpg'),
            Product(name='MacBook Pro 14-inch M3 Pro Chip 512GB SSD - Space Black', description='MacBook Pro with M3 Pro chip, 14-inch Liquid Retina XDR display, and up to 18 hours of battery life. Perfect for professional workflows and creative projects.', price=1999.00, stock_quantity=12, category_id=1, image_url='https://m.media-amazon.com/images/I/61L5QgPvgxL._AC_SX679_.jpg'),
            Product(name='Nike Air Max 270 Men\'s Running Shoes - Black/White', description='Nike Air Max 270 features the tallest Air Max unit ever for all-day comfort. Mesh upper with synthetic overlays for breathability and support.', price=150.00, stock_quantity=89, category_id=2, image_url='https://m.media-amazon.com/images/I/71Q4+8VqHVL._AC_UY695_.jpg'),
            Product(name='Adidas Originals Men\'s Trefoil Hoodie - Black', description='Classic Adidas Originals hoodie with Trefoil logo. Made from soft cotton blend with kangaroo pocket and drawstring hood. Perfect for casual wear.', price=65.00, stock_quantity=156, category_id=2, image_url='https://m.media-amazon.com/images/I/71Q4+8VqHVL._AC_UY695_.jpg'),
            Product(name='Python Crash Course, 3rd Edition: A Hands-On, Project-Based Introduction to Programming', description='Learn Python programming through hands-on projects. Covers Python basics, data structures, web applications, and data visualization. Perfect for beginners and intermediate programmers.', price=39.95, stock_quantity=203, category_id=3, image_url='https://m.media-amazon.com/images/I/71NUZ+rHN2L._AC_UY218_.jpg'),
            Product(name='Fiskars 4-Claw Garden Weeder Tool - Steel Head with Ergonomic Handle', description='Professional garden weeder with 4-claw design for efficient weed removal. Steel head with ergonomic handle for comfortable use. Ideal for maintaining healthy gardens.', price=24.97, stock_quantity=67, category_id=4, image_url='https://m.media-amazon.com/images/I/71Q4+8VqHVL._AC_UY695_.jpg'),
            Product(name='Amazon Echo Dot (5th Gen, 2022 release) - Smart speaker with Alexa - Charcoal', description='Smart speaker with Alexa. Voice control your music, get answers, and control smart home devices. Improved audio quality and built-in temperature sensor.', price=49.99, stock_quantity=312, category_id=1, image_url='https://m.media-amazon.com/images/I/714Rq4k05UL._AC_SX679_.jpg'),
            Product(name='Sony WH-1000XM5 Wireless Premium Noise Canceling Headphones - Black', description='Industry-leading noise canceling with Dual Noise Sensor technology. 30-hour battery life with quick charge. Premium sound quality and comfortable over-ear design.', price=399.99, stock_quantity=28, category_id=1, image_url='https://m.media-amazon.com/images/I/71o8Q5XJS5L._AC_SX679_.jpg'),
            Product(name='Dell XPS 13 Laptop - 13.4-inch FHD+ Display, Intel Core i7, 16GB RAM, 512GB SSD', description='Premium ultrabook with 13.4-inch InfinityEdge display, Intel Core i7 processor, 16GB RAM, and 512GB SSD. Lightweight design with all-day battery life.', price=1299.99, stock_quantity=15, category_id=1, image_url='https://m.media-amazon.com/images/I/71Q4+8VqHVL._AC_UY695_.jpg'),
            Product(name='Nike Dri-FIT Men\'s Training Shorts - Black', description='Lightweight training shorts with Dri-FIT technology to keep you dry and comfortable. Elastic waistband with drawstring and side pockets for essentials.', price=35.00, stock_quantity=178, category_id=2, image_url='https://m.media-amazon.com/images/I/71Q4+8VqHVL._AC_UY695_.jpg'),
            Product(name='The Lean Startup: How Today\'s Entrepreneurs Use Continuous Innovation', description='Eric Ries\'s methodology for building successful startups. Learn how to build a sustainable business through validated learning and rapid experimentation.', price=16.99, stock_quantity=145, category_id=3, image_url='https://m.media-amazon.com/images/I/71Q4+8VqHVL._AC_UY218_.jpg')
        ]
        for product in products:
            db.session.add(product)
        db.session.commit()
    
    # Create sample blog posts
    if Blog.query.count() == 0:
        posts = [
            Blog(title='Black Friday 2024: Best Deals on Electronics and Tech Gadgets', content='Discover the hottest Black Friday deals on smartphones, laptops, headphones, and smart home devices. Our team has curated the best offers from top brands including Apple, Samsung, Sony, and more. Save up to 70% on premium electronics this shopping season.', author='Deal Hunter Team', tags='black friday, deals, electronics, savings'),
            Blog(title='Sustainable Shopping: How to Make Eco-Friendly Purchases in 2024', content='Learn how to shop sustainably while still getting the products you love. From choosing eco-friendly brands to understanding product lifecycle, discover practical tips for reducing your environmental footprint through conscious shopping decisions.', author='Sustainability Expert', tags='sustainability, eco-friendly, shopping, environment'),
            Blog(title='Tech Trends 2024: The Gadgets That Will Define This Year', content='From AI-powered devices to foldable smartphones, explore the cutting-edge technology trends shaping 2024. Our comprehensive review covers the latest innovations in consumer electronics, smart home technology, and wearable devices.', author='Tech Innovation Team', tags='technology, trends, gadgets, innovation, 2024'),
            Blog(title='Home Office Setup Guide: Essential Products for Remote Work', content='Create the perfect home office with our curated selection of ergonomic furniture, high-quality monitors, noise-canceling headphones, and productivity tools. Transform your workspace into a professional environment that boosts productivity and comfort.', author='Workplace Solutions', tags='home office, remote work, productivity, ergonomics'),
            Blog(title='Fashion Forward: Spring 2024 Style Trends and Must-Have Items', content='Stay ahead of the fashion curve with our guide to spring 2024 trends. From sustainable fashion choices to statement pieces, discover the clothing and accessories that will define this season\'s style.', author='Fashion Editorial Team', tags='fashion, style, trends, spring 2024, clothing')
        ]
        for post in posts:
            db.session.add(post)
        db.session.commit()
    
    # Create sample newsletter subscribers
    if Newsletter.query.count() == 0:
        subscribers = [
            Newsletter(email='john.doe@example.com', name='John Doe', preferences='Electronics, Books, Weekly deals'),
            Newsletter(email='jane.smith@example.com', name='Jane Smith', preferences='Fashion, Home & Kitchen, Monthly newsletter'),
            Newsletter(email='mike.wilson@example.com', name='Mike Wilson', preferences='All categories, Daily deals, New arrivals')
        ]
        for subscriber in subscribers:
            db.session.add(subscriber)
        db.session.commit()
    
    # Create sample contact messages
    if Contact.query.count() == 0:
        contacts = [
            Contact(name='Sarah Johnson', email='sarah.j@example.com', subject='Product Inquiry', message='I am interested in learning more about your latest smartphone models and their specifications.'),
            Contact(name='David Brown', email='david.brown@example.com', subject='Shipping Question', message='Can you provide information about international shipping options and estimated delivery times?'),
            Contact(name='Lisa Davis', email='lisa.davis@example.com', subject='Return Policy', message='I would like to understand your return policy for electronics and what the process involves.')
        ]
        for contact in contacts:
            db.session.add(contact)
        db.session.commit()
    
    # Create sample reviews
    if Review.query.count() == 0:
        reviews = [
            Review(user_id=1, product_id=1, rating=5, comment='Excellent phone! Great camera quality and battery life. Highly recommended.'),
            Review(user_id=2, product_id=2, rating=4, comment='Good laptop overall, but the price could be better. Performance is solid.'),
            Review(user_id=1, product_id=3, rating=5, comment='Amazing headphones! The noise cancellation is incredible.')
        ]
        for review in reviews:
            db.session.add(review)
        db.session.commit()
    
    # Create sample orders with notes
    if Order.query.count() == 0:
        orders = [
            Order(user_id=1, total_amount=1199.00, status='completed', shipping_address='123 Main St, City, State 12345', notes='Please deliver during business hours only.'),
            Order(user_id=2, total_amount=1999.00, status='shipped', shipping_address='456 Oak Ave, City, State 67890', notes='Gift wrapping requested for this order.'),
            Order(user_id=1, total_amount=399.99, status='pending', shipping_address='789 Pine Rd, City, State 11111', notes='Customer requested expedited shipping.')
        ]
        for order in orders:
            db.session.add(order)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
