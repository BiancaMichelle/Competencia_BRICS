from flask import Flask, render_template, request, redirect, session
import json, os
from datetime import datetime
from blockchain import Blockchain

app = Flask(__name__)
app.secret_key = 'clave_secreta'

blockchain = Blockchain()

def cargar_usuarios():
    if not os.path.exists('usuarios.json'):
        return []
    with open('usuarios.json', 'r') as f:
        return json.load(f)

def guardar_usuarios(usuarios):
    with open('usuarios.json', 'w') as f:
        json.dump(usuarios, f, indent=2)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        clave = request.form["clave"]
        usuarios = cargar_usuarios()
        for u in usuarios:
            if u["usuario"] == usuario and u["clave"] == clave:
                session["usuario"] = u["usuario"]
                session["roles"] = u.get("roles", [u.get("rol")])
                return redirect("/seleccionar_rol")
        return "Credenciales incorrectas"
    return render_template("login.html")

@app.route("/seleccionar_rol")
def seleccionar_rol():
    if "usuario" not in session or "roles" not in session:
        return redirect("/")
    return render_template("seleccionar_rol.html", roles=session["roles"])

@app.route("/panel_paciente")
def panel_paciente():
    if "usuario" not in session or "paciente" not in session["roles"]:
        return redirect("/")
    usuarios = cargar_usuarios()
    usuario = next((u for u in usuarios if u["usuario"] == session["usuario"]), {})
    return render_template("panel_paciente.html", usuario=usuario)

@app.route("/panel_profesional")
def panel_profesional():
    if "usuario" not in session or "profesional" not in session["roles"]:
        return redirect("/")
    return render_template("panel_profesional.html")

@app.route("/registrar_observacion", methods=["GET", "POST"])
def registrar_observacion():
    if "usuario" not in session or "profesional" not in session["roles"]:
        return redirect("/")

    usuarios = cargar_usuarios()
    pacientes = [
    {"usuario": u["usuario"], "dni": u["dni"]}
    for u in usuarios if "paciente" in u.get("roles", [])
]

    if request.method == "POST":
        data = {
            "profesional": session["usuario"],
            "paciente": request.form["paciente"],
            "sintomas": request.form["sintomas"],
            "diagnostico": request.form["diagnostico"],
            "lugar": request.form["lugar"],
            "notas": request.form["notas"],
            "fecha": datetime.now().isoformat()
        }
        blockchain.agregar_bloque(data)
        return redirect("/panel_profesional")

    return render_template("registrar_observacion.html", pacientes=pacientes)

if __name__ == "__main__":
    app.run(debug=True)