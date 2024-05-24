import requests

url = "http://127.0.0.1:5000/predict"
# Asegúrate de que la lista de datos coincida con el número de características que tu modelo espera.
payload = {"data": [1, 2, 3, 4, 5, 6, 7]}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    # Imprimir directamente la respuesta de la API cuando la
    print(response.json())
else:
    # Imprimir el texto de error en caso de que la solicitud falle.
    print("Error al enviar la solicitud:", response.status_code)
    print(response.text)