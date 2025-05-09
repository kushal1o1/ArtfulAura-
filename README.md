# ArtfulAura-

<p align="center">
  <img src="./AA+MERGE/static_for_md/images/logo.png" alt="Project Logo" width="200" height="200">
</p>

<p align="center">
  <a href="https://github.com/kushal1o1/ArtfulAura-/stargazers"><img src="https://img.shields.io/github/stars/kushal1o1/ArtfulAura-" alt="Stars Badge"/></a>
  <a href="https://github.com/kushal1o1/ArtfulAura-/network/members"><img src="https://img.shields.io/github/forks/kushal1o1/ArtfulAura-" alt="Forks Badge"/></a>
  <a href="https://github.com/kushal1o1/ArtfulAura-/pulls"><img src="https://img.shields.io/github/issues-pr/kushal1o1/ArtfulAura-" alt="Pull Requests Badge"/></a>
  <a href="https://github.com/kushal1o1/ArtfulAura-/issues"><img src="https://img.shields.io/github/issues/kushal1o1/ArtfulAura-" alt="Issues Badge"/></a>
  <a href="https://github.com/kushal1o1/ArtfulAura-/graphs/contributors"><img alt="GitHub contributors" src="https://img.shields.io/github/contributors/kushal1o1/ArtfulAura-?color=2b9348"></a>
</p>

<p align="center">
  <b>ArtfulAura is an AI-powered online art store offering diverse artworks, secure checkout options, user reviews with sentiment analysis, and enhanced admin management.</b>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#demo">Demo</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#environment-variables">Environment Variables</a> •
  <a href="#directory-structure">Directory Structure</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a> •
  <a href="#contact">Contact</a> •
  <a href="#acknowledgments">Acknowledgments</a>
</p>


## Overview
ArtfulAura is a full-featured e-commerce platform dedicated to selling diverse forms of artwork. It combines traditional e-commerce functionality with AI-enhanced features and a user-friendly interface to deliver a premium art shopping experience.

## 🚀 Features

- **🖼️ Wide Art Categories:**  
  Supports multiple art forms:  
  Painting, Sculpture, Digital Prints, Photography, Crafts, Mixed Media, Jewelry, Textiles.

- **🔐 User Authentication:**  
  Handled via **Django Allauth**.  
  Gmail login enabled for quick and secure access.

- **🛒 Cart & Checkout System:**  
  - Add/remove products from cart.  
  - Smooth checkout process with order tracking.

- **💳 Multiple Payment Integrations:**  
  - Esewa  
  - Khalti  
  - Stripe  

- **📦 Order Management:**  
  - Email confirmation after successful payment.  
  - View complete order history.  
  - Direct refund request option from past orders.

- **📝 Review System:**  
  - Users can post product reviews and reply to others.  
  - **AI-powered sentiment analysis**:
    - Logistic Regression + TF-IDF pipeline  
    - Trained on IMDB `aclImdb` dataset  
    - 88% accuracy  
    - Hosted via Flask API on HuggingFace Spaces  
    - Triggered via Django signals after review submission

- **Coupon System**
  - Admins can add coupons with discounts 
  - users can redeem that while payments
- **🛠️ Admin Panel Enhancements:**  
  - Custom status labels like **Limited**, **Paid**, **Done**, etc.  
  - Extended admin interface for better tracking and control.



## Demo

<p align="center">
  <img src="path/to/demo.gif" alt="Demo" width="600">
</p>

## Screenshot
![Screenshot 1](./AA+MERGE/static_for_md/images/screenshot1.jpg)
![Screenshot 2](./AA+MERGE/static_for_md/images/screenshot2.jpg)
![Screenshot 3](./AA+MERGE/static_for_md/images/screenshot3.jpg)
![Screenshot 4](./AA+MERGE/static_for_md/images/screenshot4.jpg)
![Screenshot 5](./AA+MERGE/static_for_md/images/screenshot5.jpg)
![Screenshot 6](./AA+MERGE/static_for_md/images/screenshot6.jpg)
![Screenshot 7](./AA+MERGE/static_for_md/images/screenshot7.jpg)



## Installation
```bash
# Clone the repository
git clone https://github.com/kushal1o1/ArtfulAura-.git

# Navigate to the project directory
cd ArtfulAura-

pip install -r requirements.txt
```

### Prerequisites
- **Python 3.8+**

- **pip (Python package manager)**
- **Refer requirements.txt**

## Usage

```python
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```


### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `Refer` | .env.example | `for faster setup` |

## Directory Structure

```
ArtfulAura+/
├── .env.example
├── .gitignore
├── AA+MERGE/
│   ├─] .env (ignored)
│   ├── AAStore/
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   ├── core/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── services.py
│   │   ├── signals.py
│   │   ├── templatetags/
│   │   │   ├── cart_template_tags.py
│   │   │   ├── custom_filters.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── __init__.py
│   │   └── __pycache__/
│   ├── db.sqlite3
│   ├── manage.py
│   ├── media_root/
│   ├── requirements.txt
│   ├── static_for_md/
│   └── templates/
│       ├── account/
│       │   ├── account_inactive.html
│       │   ├── base.html
│       │   ├── email/
│       │   │   ├── email_confirmation_message.txt
│       │   │   ├── email_confirmation_signup_message.txt
│       │   │   ├── email_confirmation_signup_subject.txt
│       │   │   ├── email_confirmation_subject.txt
│       │   │   ├── password_reset_key_message.txt
│       │   │   └── password_reset_key_subject.txt
│       │   ├── email.html
│       │   ├── email_confirm.html
│       │   ├── login.html
│       │   ├── logout.html
│       │   ├── messages/
│       │   │   ├── cannot_delete_primary_email.txt
│       │   │   ├── email_confirmation_sent.txt
│       │   │   ├── email_confirmed.txt
│       │   │   ├── email_deleted.txt
│       │   │   ├── logged_in.txt
│       │   │   ├── logged_out.txt
│       │   │   ├── password_changed.txt
│       │   │   ├── password_set.txt
│       │   │   ├── primary_email_set.txt
│       │   │   └── unverified_primary_email.txt
│       │   ├── password_change.html
│       │   ├── password_reset.html
│       │   ├── password_reset_done.html
│       │   ├── password_reset_from_key.html
│       │   ├── password_reset_from_key_done.html
│       │   ├── password_set.html
│       │   ├── signup.html
│       │   ├── signup_closed.html
│       │   ├── snippets/
│       │   │   └── already_logged_in.html
│       │   ├── verification_sent.html
│       │   └── verified_email_required.html
│       ├── base.html
│       ├── checkout.html
│       ├── complete.html
│       ├── emails/
│       │   ├── base.html
│       │   └── notification.html
│       ├── footer.html
│       ├── home.html
│       ├── navbar.html
│       ├── order_snippet.html
│       ├── order_summary.html
│       ├── payment.html
│       ├── product_detail.html
│       ├── profile.html
│       ├── request_refund.html
│       ├── scripts.html
│       ├── socialaccount/
│       │   ├── authentication_error.html
│       │   ├── base.html
│       │   ├── connections.html
│       │   ├── login_cancelled.html
│       │   ├── messages/
│       │   │   ├── account_connected.txt
│       │   │   ├── account_connected_other.txt
│       │   │   └── account_disconnected.txt
│       │   ├── signup.html
│       │   └── snippets/
│       │       ├── login_extra.html
│       │       └── provider_list.html
│       ├── stripe_checkout.html
│       └─] test.html (ignored)
├── README.md
├── requirements.txt
├── ReviewAI/
│   ├─] .venv/ (ignored)
│   ├── model.ipynb
│   └─] review_classifier.pkl (ignored)
├── standards.md
└── TODO.py

```

## Technologies Used

<p align="center">
<img src="https://skillicons.dev/icons?i=bootstrap">
<img src="https://skillicons.dev/icons?i=sqlite">
<img src="https://skillicons.dev/icons?i=django">
<img src="https://skillicons.dev/icons?i=python">
<img src="https://skillicons.dev/icons?i=javascript">
</p>

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please make sure to update tests as appropriate and adhere to the [code of conduct](CODE_OF_CONDUCT.md).

## License

This project is licensed under the MIT License.

## Contact

Your Name - [@kushal1o1](https://twitter.com/kushal1o1) - share.kusal@.com

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/kushal1o1/MDFileCreator">MdCreator</a>
</p>