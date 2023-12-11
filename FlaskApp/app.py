from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def index():
    output = request.form.to_dict()
    question = output["question"]
    return render_template("index.html", question=question)

if __name__ == "__main__":
    app.run(debug=True, port=5001)