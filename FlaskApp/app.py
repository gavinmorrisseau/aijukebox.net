from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")
@app.route("/result", methods=["POST", "GET"])
def result():
    output = request.form.to_dict()
    result = output["result"]
    return render_template("index.html", result = result)

if __name__ == "__main__":
    app.run(debug=True, port=5001)