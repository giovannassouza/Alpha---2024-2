
import mercadopago

# Credenciais de teste
sdk = mercadopago.SDK("APP_USR-399152317369467-111409-e7711ec50d89b14605bc6f64ee5164e1-2095118211")


request = {
	"items": [
		{
			"id": "1",
			"title": "Acesso completo PlaTina",
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

print(preference)
