from flask import Flask, render_template, request
from openai import OpenAI
import time
import json
import sys

app = Flask(__name__)

def run_GPT(question=""):
    if(question not in [""]):
        question = str(request.args.get('question'))
        client = OpenAI(organization='org-1VoooiSLTr711Aax6i6A5nUT',)
        thread = client.beta.threads.create()
        assistant_id = "asst_Z8EJORrugfSAMUgxKXWNAaXw"

        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question,
        )   
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
        )
        run = wait_on_run(run, client, thread)
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        message_object = messages.data[0].content[0].text.value
        try:
            message_parsed = "FAILED"
            message_parsed = json.loads(message_object)
        except json.decoder.JSONDecodeError:
            print(f'FAILED: \n{message}')
        return(message_parsed)
    return ""

def wait_on_run(run, client, thread):
    run = request.args.get('run')
    client = request.args.get('client')
    thread = request.args.get('thread')
    while run.status in ["queued","in_progress"]:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/result", methods=["POST", "GET"])
def result():
    global message_parsed
    question = request.form.to_dict()
    message_parsed = run_GPT(question)
    return render_template("index.html", question=question, message_parsed=message_parsed)

@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404

if __name__ == "__main__":
    app.run(debug=True, port=5001)