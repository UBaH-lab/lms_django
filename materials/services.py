import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(name, description=''):
    """Создание продукта в Stripe."""
    product = stripe.Product.create(
        name=name,
        description=description,
    )
    return product.id


def create_stripe_price(amount, product_id):
    """Создание цены в Stripe (в копейках)."""
    price = stripe.Price.create(
        unit_amount=int(amount * 100),
        currency='rub',
        product=product_id,
    )
    return price.id


def create_stripe_session(price_id):
    """Создание сессии для оплаты."""
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://localhost:8000/api/payments/success/',
        cancel_url='http://localhost:8000/api/payments/cancel/',
    )
    return session


def retrieve_stripe_session(session_id):
    """Получение статуса сессии (доп. задание)."""
    return stripe.checkout.Session.retrieve(session_id)
