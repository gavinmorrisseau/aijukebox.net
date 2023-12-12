from flask import Flask, render_template, request, url_for
from openai import OpenAI
import time
import json
import sys

import traceback

app = Flask(__name__)

def run_GPT(question):
    print("RUNNING GPT")
    print("QUESTION: " + question)
    if(question not in ["",None,'']):
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
        message_parsed = "FAILED"
        try:
            message_parsed = json.loads(message_object)
        except json.decoder.JSONDecodeError:
            print(f'FAILED: \n{message}')
        print("COMPLETED GPT")
        return(message_parsed)
    print("CANCELLED GPT")
    return ""

def wait_on_run(run, client, thread):
    while run.status in ["queued","in_progress"]:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.25)
    return run

@app.route('/', methods = ['POST','GET'])
def index():
    # if request.method == 'GET':
    #     pass
    question = ''
    message_parsed = ''
    if request.method in ['POST','GET'] and request.form.get('question') != '':
        question = request.form.to_dict().get('question','')
        #print("BEHIND QUESTION: " + str(question))
        if(question not in ["",None]):
            message_parsed = run_GPT(question)
        else:
            message_parsed = ''
        #print("BEHIND MSG PARSED: " + str(message_parsed))
    return render_template("index.html", question=question, message_parsed=message_parsed)

@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404

if __name__ == "__main__":
    app.run(debug=True, port=5001)