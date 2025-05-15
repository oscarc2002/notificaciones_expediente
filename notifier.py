from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configuración de la API de WhatsApp Cloud
WHATSAPP_TOKEN = ""
PHONE_NUMBER_ID = "552863861251163"
WHATSAPP_API_URL = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

HEADERS = {
    "Authorization": f"Bearer {WHATSAPP_TOKEN}",
    "Content-Type": "application/json"
}   

plantillas = {
    "notificacion_cita": ["message"],
    "notificacion_reporte": ["name", "email"]
}

@app.route('/send-message', methods=['POST'])
def send_message():
    try:
        data = request.get_json()
        template = data.get("template")
        phones = data.get("phones", [])
        params = data.get("params", [])

        if not template or not phones:
            return jsonify({"error": "Faltan campos obligatorios (template o phone)"}), 400

        if template not in plantillas:
            return jsonify({"error": f"Plantilla '{template}' no está registrada"}), 400

        cant_params = plantillas[template]
        if len(cant_params) != len(params):
            return jsonify({"error": f"La plantilla '{template}' requiere {len(cant_params)} parámetros, se recibieron {len(params)}"}), 400

        results = []
        for phone in phones:
            payload = {
                "messaging_product": "whatsapp",
                "to": phone,
                "type": "template",
                "template": {
                    "name": template,
                    "language": {"code": "es"},
                    "components": [
                        {
                            "type": "body",
                            "parameters": [{"type": "text", "text": value} for value in params]
                        }
                    ]
                }
            }
            response = requests.post(WHATSAPP_API_URL, json=payload, headers=HEADERS)
            results.append({
                "to": phone,
                "status_code": response.status_code,
                "response": response.json()
            })

        return jsonify({"results": results}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3000)
    