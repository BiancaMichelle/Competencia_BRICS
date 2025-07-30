from flask import Flask, render_template, request, redirect, session
import json
from blockchain import Blockchain
import hashlib

app = Flask(__name__)
app.secret_key = 'secreto'
bc = Blockchain()


def cargar_usuarios():
    with open("usuarios.json", "r") as f:
        return json.load(f)

def firmar(usuario, clave):
    return hashlib.sha256(f"{usuario}:{clave}".encode()).hexdigest()

@app.route('/')
def inicio():
    if 'usuario' in session:
        return redirect('/registro')
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form['usuario']
    clave = request.form['clave']
    usuarios = cargar_usuarios()
    for u in usuarios:
        if u["usuario"] == usuario and u["clave"] == clave:
            session['usuario'] = usuario
            session['rol'] = u["rol"]
            session['clave'] = clave
            return redirect('/registro')
    return "Login incorrecto"

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if 'usuario' not in session:
        return redirect('/')

    if request.method == 'POST':
        paciente = request.form['paciente']
        descripcion = request.form['descripcion']
        firma = firmar(session['usuario'], session['clave'])
        data = {
            "paciente": paciente,
            "profesional": session['usuario'],
            "descripcion": descripcion
        }
        bc.agregar_bloque(data, firma)
        return redirect('/cadena')

    return render_template('registro.html', usuario=session['usuario'], rol=session['rol'])

@app.route('/cadena')
def ver_cadena():
    return render_template('cadena.html', bloques=bc.cadena, valida=bc.es_valida())

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
