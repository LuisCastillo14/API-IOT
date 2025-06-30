from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Estructuras de control
estado_leds = {f"led{i}": "apagar" for i in range(1, 7)}
temporizadores = {f"led{i}": None for i in range(1, 7)}  # segundos
horarios_programados = {f"led{i}": None for i in range(1, 7)}  # formato "HH:MM"

# === ENDPOINT para control inmediato (encender/apagar con opcional temporizador) ===
@app.route("/actualizar-led", methods=["POST"])
def actualizar_led():
    data = request.get_json()
    led = data.get("led")
    accion = data.get("accion")
    temporizador = data.get("temporizador")

    if led in estado_leds and accion in ["encender", "apagar"]:
        estado_leds[led] = accion
        if temporizador is not None:
            try:
                temporizadores[led] = int(temporizador)
            except ValueError:
                return jsonify({"status": "error", "mensaje": "Temporizador inválido"}), 400
        else:
            temporizadores[led] = None

        return jsonify({"status": "ok", "led": led, "accion": accion, "temporizador": temporizadores[led]})
    else:
        return jsonify({"status": "error", "mensaje": "Entrada inválida"}), 400

# === ENDPOINT para programar encendido automático a una hora ===
@app.route("/programar-led", methods=["POST"])
def programar_led():
    data = request.get_json()
    led = data.get("led")
    hora = data.get("hora")

    if led not in horarios_programados:
        return jsonify({"status": "error", "mensaje": "LED inválido"}), 400

    try:
        datetime.strptime(hora, "%H:%M")  # Validación de formato
    except ValueError:
        return jsonify({"status": "error", "mensaje": "Formato de hora inválido (use HH:MM)"}), 400

    horarios_programados[led] = hora
    return jsonify({"status": "ok", "led": led, "hora_programada": hora})

# === ENDPOINT para lectura por ESP32 ===
@app.route("/comando", methods=["GET"])
def obtener_comandos():
    salida = {}
    for i in range(1, 7):
        led_id = f"led{i}"
        salida[led_id] = estado_leds[led_id]
        salida[f"temporizador_{led_id}"] = temporizadores[led_id]
        salida[f"hora_programada_{led_id}"] = horarios_programados[led_id]
    return jsonify(salida)

# === HOME ===
@app.route("/")
def home():
    return "API de control de LEDs (ESP32 + Temporizador + Programación)"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
