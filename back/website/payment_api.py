import mercadopago
from .api_key import mercadoPago_key
from . import app_url
#   Existe um problema no back_urls, por estar em localhost o retorno dá um erro,
#   isso é previsto no site mas deve arrumar quando fizermos o deploy

back_urls= {
            "success": app_url +"/payment_done",
            "failure": app_url +"/payment_denied",
            "pending": app_url +"/payment_denied",
        }

def create_payment_anual():
    """
    Create an annual payment preference using MercadoPago.
    ---
    tags:
      - Payments
    responses:
      200:
        description: URL of the preference created to be paid.
    """
    sdk = mercadopago.SDK(mercadoPago_key)

    request = {
        "items": [
            {
                "id": "1",
                "title": "Acesso completo PlaTina - 1 ANO",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": 123.45,

            },
        ],
        "back_urls": back_urls,
        "auto_return": "all",
        
    }

    preference_response = sdk.preference().create(request)
    preference = preference_response["response"]
    payment_link = preference["init_point"]

    return payment_link


def create_payment_monthly():
    """
    Create a monthly payment preference using MercadoPago.
    ---
    tags:
      - Payments
    responses:
      200:
        description: URL of the preference created to be paid.
    """
    sdk = mercadopago.SDK(mercadoPago_key)

    request = {
        "items": [
            {
                "id": "2",
                "title": "Acesso completo PLATINA - 1 MÊS",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": 42.83,
            },
        ],
        "back_urls": back_urls,
        "auto_return": "all",
        
    }

    preference_response = sdk.preference().create(request)
    preference = preference_response["response"]
    payment_link = preference["init_point"]
    
    return payment_link

def create_payment_eternal():
    """
    Create a lifetime payment preference using MercadoPago.
    ---
    tags:
      - Payments
    responses:
      200:
        description: URL of the preference created to be paid.
    """
    sdk = mercadopago.SDK(mercadoPago_key)

    request = {
        "items": [
            {
                "id": "3",
                "title": "Acesso completo PlaTina - VITALÍCIO",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": 234.83,
            },
        ],
        "back_urls": back_urls,
        "auto_return": "all",
        
    }

    preference_response = sdk.preference().create(request)
    preference = preference_response["response"]
    payment_link = preference["init_point"]
    
    return payment_link

create_payment_eternal()