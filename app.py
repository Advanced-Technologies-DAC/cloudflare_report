"""
Backend
"""

from flask import Flask, render_template, send_from_directory, request

app = Flask(__name__)


@app.route("/")
def homeTEST():
    """
    Home route
    """
    return render_template("base.html")


@app.route("/admin")
def admin():
    """
    Admin route
    """
    return render_template("admin.html")


@app.route("/reporte")
def reporte():
    """
    Reporte route
    """
    return render_template("reporte.html")

@app.route("/get_report")
def get_reporte():
    """
    Crear un reporte
    """
    client = request.args.get("client")
    period = request.args.get("period")
    
    if not client or not period:
        return "<p style='color: red;'>Error: Cliente y período requeridos</p>", 400
    return "<p style='color: green;'>Reporte generado.</p>", 200


@app.route("/user")
def user():
    """
    User route
    """
    return render_template("user.html")


@app.route("/download/report")
def download_report():
    return send_from_directory(
        directory="assets", path="report.pdf", as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True, port=5002)
