from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import hashlib
import time

app = Flask(__name__)
app.secret_key = "supersecreto123"

# =======================
# Funciones de usuario
# =======================
def cargar_usuarios():
    with open("usuarios.json", "r", encoding="utf-8") as f:
        return json.load(f)

def verificar_usuario(usuario, clave):
    usuarios = cargar_usuarios()
    clave_hash = hashlib.sha256(clave.encode()).hexdigest()
    for u in usuarios:
        if u['usuario'] == usuario and hashlib.sha256(u['clave'].encode()).hexdigest() == clave_hash:
            return u
    return None

# =======================
# Blockchain simulado
# =======================
def cargar_blockchain():
    try:
        with open("blockchain.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def guardar_blockchain(chain):
    with open("blockchain.json", "w", encoding="utf-8") as f:
        json.dump(chain, f, indent=4)

def registrar_login_blockchain(usuario):
    chain = cargar_blockchain()
    timestamp = time.time()
    # Simple hash del bloque anterior
    previous_hash = chain[-1]['hash'] if chain else "0"*64
    block_data = f"{usuario}{timestamp}{previous_hash}".encode()
    block_hash = hashlib.sha256(block_data).hexdigest()
    bloque = {
        "usuario": usuario,
        "timestamp": timestamp,
        "previous_hash": previous_hash,
        "hash": block_hash
    }
    chain.append(bloque)
    guardar_blockchain(chain)

# =======================
# Rutas
# =======================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        clave = request.form["clave"]
        user = verificar_usuario(usuario, clave)
        if user:
            # Registrar login en blockchain
            registrar_login_blockchain(usuario)
            
            # Guardar en sesión
            session["usuario"] = user["usuario"]
            session["roles"] = user["roles"]
            session["nombre_medico"] = user["nombre"]  # Guardamos el nombre
            flash(f"¡Bienvenido {user['usuario']}!", "success")

            # Redirigir según rol
            if "profesional" in user["roles"]:
                return redirect(url_for("panel_profesional"))
            elif "paciente" in user["roles"]:
                return redirect(url_for("panel_paciente"))
        else:
            flash("Usuario o clave incorrectos", "error")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/panel_paciente")
def panel_paciente():
    if "usuario" not in session:
        return redirect(url_for("login"))
    if "paciente" not in session["roles"]:
        return "Acceso denegado"
    return render_template("panel_paciente.html", usuario=session["usuario"])

@app.route("/panel_profesional")
def panel_profesional():
    if "usuario" not in session:
        return redirect(url_for("login"))
    if "profesional" not in session["roles"]:
        return "Acceso denegado"
    nombre_medico = session.get("nombre_medico", "Médico")  # si no está en sesión, usa "Médico"
    return render_template("panel_profesional.html", nombre_medico=nombre_medico)

import json
from flask import jsonify

@app.route("/api/pacientes")
def api_pacientes():
    usuarios = cargar_usuarios()
    pacientes_resumen = []
    for u in usuarios:
        if "paciente" in u.get("roles", []):
            pacientes_resumen.append({
                "id": u.get("id"),
                "nombre": u.get("nombre"),
                "ci": u.get("ci"),
                # Usamos el último diagnóstico como enfermedad actual
                "enfermedad_actual": u.get("diagnosticos", [])[-1] if u.get("diagnosticos") else "No especificada"
            })
    return jsonify(pacientes_resumen)

# Detalle completo de un paciente
@app.route("/api/pacientes/<int:paciente_id>")
def api_paciente_detalle(paciente_id):
    usuarios = cargar_usuarios()
    paciente = next((u for u in usuarios if u.get("id") == paciente_id), None)
    if not paciente:
        return jsonify({"error": "Paciente no encontrado"}), 404
    return jsonify(paciente)

@app.route("/logout")
def logout():
    session.clear()  # Limpiar toda la sesión
    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for("login"))  # Redirigir al login

if __name__ == "__main__":
    app.run(debug=True)
