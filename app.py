from flask import Flask, render_template, request
from flask import redirect, url_for, session, flash
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from conexion import conectar

import os
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "solo-para-desarrollo-local"),
    SESSION_COOKIE_SECURE="SECRET_KEY" in os.environ,  # solo HTTPS en producción
)

@app.route("/dbtest")
def dbtest():
    info = {"DATABASE_URL_definida": "DATABASE_URL" in os.environ}
    try:
        c = conectar()
        cur = c.cursor()
        cur.execute("SHOW TABLES")
        info["conexion"] = "OK"
        info["tablas"] = [t[0] for t in cur.fetchall()]
        cur.close()
        c.close()
    except Exception as e:
        info["conexion"] = "FALLO"
        info["error"] = f"{type(e).__name__}: {e}"
    return info

# LOGIN
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT id, password FROM usuarios WHERE usuario=%s",
            (usuario,)
        )

        resultado = cursor.fetchone()
        cursor.close()
        conexion.close()

        if resultado and clave_correcta(resultado[1], password):
            session.clear()
            session["usuario"] = usuario
            return redirect(url_for("mascotas"))

        flash("Usuario o contraseña incorrectos")

    return render_template("login.html")


# CONSULTAR MASCOTAS
@app.route("/mascotas")
def mascotas():
    if "usuario" not in session:
        return redirect(url_for("login"))

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM mascotas")
    datos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template("mascotas.html", mascotas=datos)


# REGISTRAR MASCOTA
@app.route("/registrar", methods=["POST"])
def registrar():
    if "usuario" not in session:
        return redirect(url_for("login"))

    nombre = request.form["nombre"].strip()
    especie = request.form["especie"].strip()
    raza = request.form["raza"].strip()
    propietario = request.form["propietario"].strip()

    try:
        edad = int(request.form["edad"])

        if not nombre or not especie or not propietario or edad < 0:
            raise ValueError

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO mascotas
            (nombre, especie, raza, edad, propietario)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, especie, raza, edad, propietario))

        conexion.commit()
        cursor.close()
        conexion.close()

        flash("Mascota registrada correctamente")

    except ValueError:
        flash("Verifica los datos y la edad")

    return redirect(url_for("mascotas"))


# ACTUALIZAR MASCOTA
@app.route("/actualizar/<int:id>", methods=["POST"])
def actualizar(id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    try:
        nombre = request.form["nombre"].strip()
        especie = request.form["especie"].strip()
        raza = request.form["raza"].strip()
        propietario = request.form["propietario"].strip()
        edad = int(request.form["edad"])

        if not nombre or not especie or not propietario or edad < 0:
            raise ValueError

        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE mascotas
            SET nombre=%s, especie=%s, raza=%s, edad=%s, propietario=%s
            WHERE id=%s
        """, (nombre, especie, raza, edad, propietario, id))

        conexion.commit()
        cursor.close()
        conexion.close()

        flash("Mascota actualizada correctamente")

    except ValueError:
        flash("Verifica los datos ingresados")

    return redirect(url_for("mascotas"))


# ELIMINAR MASCOTA
@app.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    if "usuario" not in session:
        return redirect(url_for("login"))

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM mascotas WHERE id=%s", (id,))

    conexion.commit()
    cursor.close()
    conexion.close()

    flash("Mascota eliminada correctamente")

    return redirect(url_for("mascotas"))


# CERRAR SESIÓN
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/healthz")
def health():
    return "Sistema veterinario funcionando", 200

def clave_correcta(guardada, ingresada):
    try:
        return check_password_hash(guardada, ingresada)
    except ValueError:
        return False
    
if __name__ == "__main__":
    app.run(debug=True)