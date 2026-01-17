from flask import Flask, send_from_directory

app = Flask(__name__, static_folder=".")

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/logo.png")
def logo():
    return send_from_directory(".", "logo.png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
