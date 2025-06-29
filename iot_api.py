from flask import Flask, request, jsonify

app = Flask(__name__)

# Estados de los 6 LEDs, por defecto todos apagados
estado_leds = {
    "led1": "apagar",
    "led2": "apagar",
    "led3": "apagar",
    "led4": "apagar",
    "led5": "apagar",
    "led6": "apagar"
}

@app.route("/actualizar-led", methods=["POST"])
def actualizar_led():
    data = request.get_json()
    led = data.get("led")    # led1, led2, ...
    accion = data.get("accion")  # encender / apagar

    if led in estado_leds and accion in ["encender", "apagar"]:
        estado_leds[led] = accion
        return jsonify({"status": "ok", "led": led, "accion": accion})
    else:
        return jsonify({"status": "error", "mensaje": "Entrada inválida"}), 400

@app.route("/comando", methods=["GET"])
def obtener_comandos():
    return jsonify(estado_leds)

@app.route("/")
def home():
    return "API de control de LEDs (ESP32)"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)