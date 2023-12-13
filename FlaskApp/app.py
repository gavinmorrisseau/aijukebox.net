import time
import json
import traceback
from flask import Flask, render_template, request
from openai import OpenAI

# OpenAI API Setup
client = OpenAI(organization='org-1VoooiSLTr711Aax6i6A5nUT',)
thread = client.beta.threads.create()
assistant_id = "asst_Z8EJORrugfSAMUgxKXWNAaXw"

# JSON Placeholder Response
placeholder_response = {'1': {'artist': '', 'track': ''},
                        '2': {'artist': '', 'track': ''},
                        '3': {'artist': '', 'track': ''},
                        '4': {'artist': '', 'track': ''},
                        '5': {'artist': '', 'track': ''}}

app = Flask(__name__)

def run_gpt(question):
    ''' Synchronous Run for GPT4 Assistant Response for Question '''

    # Debug
    print("RUNNING GPT")
    print("QUESTION: " + question)

    # Synchronous Run
    run = client.beta.threads.runs.create(thread_id=thread.id,assistant_id=assistant_id,)
    run = wait_on_run(run, client, thread)

    # Parse Response
    latest_message = client.beta.threads.messages.list(thread_id=thread.id, order="asc")
    print(latest_message) # DEBUG
    message_string = latest_message.data[0].content[0].text.value

    # Return Response
    try:
        message_parsed = json.loads(message_string)
        print("ANSWER: " + str(message_parsed)) # DEBUG
        return message_parsed
    except json.decoder.JSONDecodeError:
        print("FAILED! placeholder_response used") # DEBUG
        return placeholder_response

def wait_on_run(run, client, thread):
    ''' Syncronous Run Helper Function ''' 
    while run.status in ["queued","in_progress"]:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.2)
    return run

@app.route('/', methods = ['POST','GET'])
def index():
    ''' /index Route'''
    # Definitions
    question = ''
    answer = ''

    # Run GPT if conditions are met
    if request.method in ['POST'] and request.form.get('question') not in '':
        question = request.form.to_dict().get('question')
        answer = run_gpt(question)
    else:
        answer = placeholder_response
    
    #Render index.html
    return render_template("index.html", question=question, answer=answer, placeholder_response=placeholder_response)

@app.errorhandler(404)
def page_not_found(error):
    ''' 404 Error Handler '''
    return 'This page does not exist', 404

if __name__ == "__main__":
    app.run(debug=True, port=5001)
