# Daisy Dreams - Flower Shop E-commerce Website

A full-featured e-commerce website for a flower shop built with Django and Tailwind CSS. Similar to Flipkart/Shopify with all essential features.

## Features

### 🛒 E-commerce Features

- Product catalog with categories and filters
- Shopping cart with quantity management
- Wishlist functionality
- Coupon/discount system
- Order tracking

### 🌸 Product Features

- Categories by occasion (Marriage, Birthday, Anniversary, etc.)
- Product variants (sizes)
- Product reviews and ratings
- Same-day delivery options
- Related products

### 💳 Payment Integration

- Razorpay payment gateway
- Cash on Delivery
- Secure payment processing

### 👤 User Features

- User registration and authentication
- User dashboard
- Address management
- Order history
- Profile management

### 🎨 Design

- Beautiful Tailwind CSS design
- Responsive for all devices
- Smooth animations with AOS
- Modern UI/UX

## Installation

### Prerequisites

- Python 3.10+
- pip

### Setup

1. **Clone or download the project**

2. **Create virtual environment**

   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   ```bash
   # Copy example env file
   copy .env.example .env

   # Edit .env with your settings
   ```

5. **Run migrations**

   ```bash
   python manage.py makemigrations shop cart orders payments accounts
   python manage.py migrate
   ```

6. **Create superuser**

   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**

   ```bash
   python manage.py runserver
   ```

8. **Access the website**
   - Website: http://127.0.0.1:8000
   - Admin: http://127.0.0.1:8000/admin

## Adding Sample Data

1. Login to admin panel
2. Add Categories (Marriage, Birthday, Anniversary, etc.)
3. Add Flower Types (Roses, Lilies, Orchids, etc.)
4. Add Products with images
5. Add Banners for homepage

## Project Structure

```
flower_shop/
├── flower_shop/          # Main project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── shop/                 # Products, categories
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── cart/                 # Shopping cart
│   ├── cart.py
│   ├── views.py
│   └── urls.py
├── orders/               # Orders and checkout
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── payments/             # Payment processing
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── accounts/             # User authentication
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── templates/            # HTML templates
├── static/               # CSS, JS, images
├── media/               # User uploads
├── manage.py
└── requirements.txt
```

## Payment Gateway Setup

### Razorpay

1. Create account at https://razorpay.com
2. Get API keys from Dashboard
3. Add to `.env` file:
   ```
   RAZORPAY_KEY_ID=rzp_test_xxxx
   RAZORPAY_KEY_SECRET=xxxx
   ```

## Customization

### Adding New Categories

1. Go to Admin > Shop > Categories
2. Add category with name, slug, occasion, and image

### Adding New Products

1. Go to Admin > Shop > Products
2. Fill in all details including images
3. Set featured/bestseller flags for homepage display

## Technologies Used

- **Backend**: Django 5.0
- **Frontend**: Tailwind CSS (via CDN)
- **Database**: SQLite (development)
- **Payment**: Razorpay
- **Icons**: Font Awesome
- **Animations**: AOS (Animate on Scroll)
- **Fonts**: Google Fonts (Inter, Playfair Display)

## License

MIT License

## Support

For support, email support@Daisy Dreams.com or create an issue.
