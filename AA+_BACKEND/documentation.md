
# Project Documentation: ArtfulAura+ E-commerce Store

## Objective:
Develop a fully functional, professional e-commerce platform that sells artistic stickers, wall posters, frames, and more. The project will include search functionality, payment integration, categories, trending products, discounts, reviews, comments, ratings, and more.

---

## 1. Apps Structure:

- **users**: User management (registration, login, profile).
- **products**: Product catalog and categories.
- **orders**: Shopping cart, checkout, and order management.
- **reviews**: Product reviews and ratings.
- **discounts**: Discount codes and promotions.
- **payments**: Payment gateway integration.
- **wishlist**: User's saved products for later.
- **shipping**: Shipping details and tracking.
- **dashboard**: Admin panel for managing products, orders, users, etc.

---

## 2. Models and Fields:

### users (User Management):
- **UserProfile**: 
  - `user (OneToOneField)`: Link to Django's built-in User model.
  - `shipping_address (TextField)`.
  - `phone_number (CharField)`.

### products (Product Catalog):
- **Product**:
  - `name (CharField)`.
  - `description (TextField)`.
  - `price (DecimalField)`.
  - `category (ForeignKey)` – Category of the product.
  - `tags (ManyToManyField)` – Tags for filtering and searching.
  - `image (ImageField)`.

- **Category**:
  - `name (CharField)`.

### orders (Order Management):
- **Order**:
  - `user (ForeignKey)` – Reference to the user.
  - `items (ManyToManyField)` – Products in the order.
  - `total_amount (DecimalField)`.
  - `status (CharField)` – Pending, Delivered, etc.

### reviews (Reviews and Ratings):
- **Review**:
  - `user (ForeignKey)`.
  - `product (ForeignKey)`.
  - `rating (IntegerField)` – 1-5 rating.
  - `comment (TextField)`.

### discounts (Discount Codes):
- **Discount**:
  - `code (CharField)` – The discount code.
  - `discount_percentage (IntegerField)`.

### payments (Payment Integration):
- **Payment**:
  - `user (ForeignKey)`.
  - `order (ForeignKey)`.
  - `status (CharField)` – Success, Failed, etc.

---

## 3. API Endpoints (RESTful API):

### users:
- `POST /api/users/register/` – User registration.
- `POST /api/users/login/` – User login.
- `GET /api/users/profile/` – Get user profile.
- `PUT /api/users/profile/update/` – Update profile.

### products:
- `GET /api/products/` – List all products.
- `GET /api/products/<id>/` – Product detail.
- `POST /api/products/` – Add a product (Admin only).
- `PUT /api/products/<id>/` – Edit product (Admin only).
- `DELETE /api/products/<id>/` – Delete product (Admin only).

### orders:
- `POST /api/orders/` – Create a new order.
- `GET /api/orders/<id>/` – Get order details.
- `PUT /api/orders/<id>/` – Update order status (Admin).

### reviews:
- `POST /api/products/<id>/reviews/` – Add a review to a product.
- `GET /api/products/<id>/reviews/` – Get all reviews for a product.

### discounts:
- `POST /api/discounts/apply/` – Apply a discount code at checkout.

### payments:
- `POST /api/payments/` – Process payment.
- `GET /api/payments/status/` – Check payment status.

---

## 4. User Interface:

- **Homepage**:
  - Display featured products, trending categories, and search bar.
  
- **Product Page**:
  - Product details, reviews, ratings, and related products.
  
- **Cart and Checkout**:
  - Cart summary with product details and total price.
  - Apply discount code and proceed to payment.

- **Admin Dashboard**:
  - Manage products, orders, reviews, and discounts.

---

## 5. Features and Functionalities:

- **User Authentication**: 
  - Secure registration, login, and profile management.
  
- **Product Management**: 
  - Admin can add, edit, and delete products. Users can browse products by categories or search by tags.

- **Shopping Cart**:
  - Users can add products to the cart, update quantities, and proceed to checkout.

- **Payment Gateway Integration**:
  - Stripe or PayPal for secure payments.

- **Discount Codes**:
  - Apply discount codes for price reduction during checkout.

- **Order Management**:
  - Users can view their order history and track order status.

---

## 6. Next Steps:

- Start by creating the **User Authentication** system.
- Setup **Product** models and API endpoints.
- Develop the **Order and Cart** functionality.
- Integrate **Payment Gateway**.
- Add **Review**, **Rating**, and **Discount** features.
