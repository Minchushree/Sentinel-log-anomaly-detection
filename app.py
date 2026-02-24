from flask import Flask, render_template, jsonify
from dashboard.metrics_manager import read_metrics

app = Flask(__name__)

@app.route("/")
def dashboard():
    return render_template("index.html")

@app.route("/advanced")
def advanced_dashboard():
    return render_template("advanced_dashboard.html")

@app.route("/metrics")
def metrics():
    return jsonify(read_metrics())

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
