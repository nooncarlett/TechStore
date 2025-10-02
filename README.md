# TechStore Pro - E-commerce Platform

A professional e-commerce platform built with Flask, featuring a modern Amazon-like design with realistic product data. Perfect for learning web development and e-commerce functionality.

## 🚀 Features

- **Professional E-commerce Design**: Amazon-like interface with modern UI/UX
- **User Authentication**: Registration, login, and profile management
- **Product Catalog**: Browse products by category with detailed descriptions
- **Shopping Cart**: Add/remove items and manage quantities
- **Order Management**: Complete checkout process and order tracking
- **Admin Panel**: Manage products, users, orders, and content
- **Blog System**: Create and manage blog posts
- **Contact & Newsletter**: Contact forms and newsletter subscriptions
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## 🛠 Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **Authentication**: Werkzeug Security
- **Styling**: Custom CSS with Amazon-like design

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd techstore-pro
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser and go to `http://127.0.0.1:5001`

## 🔐 Default Credentials

- **Admin Account**: 
  - Username: `admin`
  - Password: `admin123`

- **Test User Account**:
  - Username: `testuser`
  - Password: `password123`

## 📊 Sample Data

The application comes pre-populated with:
- **12 Products** across 4 categories (Electronics, Clothing, Books, Home & Kitchen)
- **4 Categories** with detailed descriptions
- **5 Blog Posts** covering various topics
- **3 Newsletter Subscribers** with different preferences
- **3 Contact Messages** from customers
- **3 Product Reviews** with ratings and comments
- **3 Orders** with notes and shipping information

## 🎓 Educational Use

This project is designed for:
- **Web Development Learning**: Understand Flask framework and e-commerce development
- **Database Design**: Learn about SQLAlchemy ORM and database relationships
- **Frontend Development**: Practice HTML, CSS, and JavaScript
- **Full-Stack Development**: Complete web application development

## 📁 Project Structure

```
techstore-pro/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── .gitignore            # Git ignore file
├── static/
│   └── css/
│       └── style.css     # Custom styling
└── templates/
    ├── base.html         # Base template
    ├── index.html        # Homepage
    ├── products.html     # Product listing
    ├── product_detail.html # Product details
    ├── login.html        # User login
    ├── register.html     # User registration
    ├── profile.html      # User profile
    ├── cart.html         # Shopping cart
    ├── checkout.html     # Checkout process
    ├── orders.html       # Order history
    ├── contact.html      # Contact form
    ├── blog.html         # Blog listing
    ├── blog_post.html    # Individual blog post
    ├── search.html       # Search results
    └── admin/
        ├── dashboard.html # Admin dashboard
        ├── products.html  # Product management
        ├── users.html     # User management
        ├── orders.html    # Order management
        ├── reviews.html   # Review management
        ├── newsletter.html # Newsletter management
        ├── contacts.html  # Contact management
        └── blog.html      # Blog management
```

## 🔧 Configuration

The application uses the following default configuration:
- **Port**: 5001
- **Database**: SQLite (ecommerce.db)
- **Secret Key**: Change in production
- **Debug Mode**: Enabled for development

## 📈 Features Overview

### User Features
- Browse products by category
- Search products and blog posts
- Add products to shopping cart
- Complete purchase process
- View order history
- Write product reviews
- Manage user profile
- Subscribe to newsletter
- Contact support

### Admin Features
- Dashboard with statistics
- Product management (add, edit, delete)
- Category management
- Order management and status updates
- User management
- Review moderation
- Newsletter subscriber management
- Contact message management
- Blog post management

## 🚀 Deployment

### Production Considerations
1. Change the secret key in `app.py`
2. Use a production database (PostgreSQL, MySQL)
3. Set `debug=False` in production
4. Use a production WSGI server (Gunicorn, uWSGI)
5. Configure proper logging and monitoring

### Environment Variables
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here
export DATABASE_URL=your-database-url
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.