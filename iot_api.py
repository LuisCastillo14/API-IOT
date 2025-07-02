from flask import Flask, request, jsonify
from datetime import datetime
import threading
import time
from flask_cors import CORS 

app = Flask(__name__)
CORS(app)     

# === Estados globales ===
estado_leds = {f"led{i}": "apagar" for i in range(1, 7)}
temporizadores = {f"led{i}": None for i in range(1, 7)}  # segundos
horarios_programados = {f"led{i}": {"hora": None, "accion": None} for i in range(1, 7)}


# === Endpoint para control inmediato ===
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

# === Endpoint para programar encendido automático ===
@app.route("/programar-led", methods=["POST"])
def programar_led():
    data = request.get_json()
    led = data.get("led")
    hora = data.get("hora")
    accion = data.get("accion")  # NUEVO

    if led not in horarios_programados:
        return jsonify({"status": "error", "mensaje": "LED inválido"}), 400

    try:
        datetime.strptime(hora, "%H:%M")
    except ValueError:
        return jsonify({"status": "error", "mensaje": "Formato de hora inválido (use HH:MM)"}), 400

    if accion not in ["encender", "apagar"]:
        return jsonify({"status": "error", "mensaje": "Acción inválida"}), 400

    horarios_programados[led] = {"hora": hora, "accion": accion}
    return jsonify({"status": "ok", "led": led, "hora_programada": hora, "accion": accion})


# === Endpoint que el ESP32 consulta cada 2 segundos ===
@app.route("/comando", methods=["GET"])
def obtener_comandos():
    salida = {}
    for i in range(1, 7):
        led_id = f"led{i}"
        salida[led_id] = estado_leds[led_id]
        salida[f"temporizador_{led_id}"] = temporizadores[led_id]
        prog = horarios_programados[led_id]
        salida[f"hora_programada_{led_id}"] = prog["hora"] if prog else None
        salida[f"accion_programada_{led_id}"] = prog["accion"] if prog else None
    return jsonify(salida)

@app.route("/")
def home():
    return "API de control de LEDs (ESP32 + Temporizador + Programación)"

def verificador_programacion():
    while True:
        ahora = datetime.now().strftime("%H:%M")
        for led, info in horarios_programados.items():
            if info["hora"] == ahora:
                estado_leds[led] = info["accion"]
                print(f"[AUTO] {led} {info['accion']} automáticamente a las {info['hora']}")
        time.sleep(60)

# === Iniciar hilo de fondo al arrancar la API ===
if __name__ == "__main__":
    hilo = threading.Thread(target=verificador_programacion)
    hilo.daemon = True  # Hilo en segundo plano
    hilo.start()

    app.run(host="0.0.0.0", port=5000)
