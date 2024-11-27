import mercadopago
#   Existe um problema no back_urls, por estar em localhost o retorno dá um erro,
#   isso é previsto no site mas deve arrumar quando fizermos o deploy

# CREDENCIAIS DE TESTE, NÃO TENTE REFAZER
key = "APP_USR-399152317369467-111409-e7711ec50d89b14605bc6f64ee5164e1-2095118211"

def create_payment_anual():
    # Credenciais de teste
    sdk = mercadopago.SDK(key)

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
        "back_urls": {
            "success": "https://127.0.0.1:5000/payment_done",
            "failure": "https://127.0.0.1:5000/payment_denied",
            "pending": "https://127.0.0.1:5000/payment_denied",
        },
        "auto_return": "all",
        
    }

    preference_response = sdk.preference().create(request)
    preference = preference_response["response"]
    payment_link = preference["init_point"]

    return payment_link


def create_payment_monthly():
    # Credenciais de teste
    sdk = mercadopago.SDK(key)

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
        "back_urls": {
            "success": "https://127.0.0.1:5000/payment_done",
            "failure": "https://127.0.0.1:5000/payment_denied",
            "pending": "https://127.0.0.1:5000/payment_denied",
        },
        "auto_return": "all",
        
    }

preference_response = sdk.preference().create(request)
preference = preference_response["response"]

print(preference)
