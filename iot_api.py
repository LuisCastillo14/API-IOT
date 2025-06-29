from flask import Flask, request, jsonify

app = Flask(__name__)
ultimo_comando = None  # Variable global (sin base de datos)

@app.route("/enviar-comando", methods=["POST"])
def enviar_comando():
    global ultimo_comando
    data = request.get_json()
    comando = data.get("comando")
    if comando in ["encender", "apagar"]:
        ultimo_comando = comando
        return jsonify({"status": "ok", "comando": comando})
    return jsonify({"status": "error", "mensaje": "Comando inválido"}), 400

@app.route("/comando", methods=["GET"])
def obtener_comando():
    global ultimo_comando
    return jsonify({"comando": ultimo_comando or "ninguno"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)