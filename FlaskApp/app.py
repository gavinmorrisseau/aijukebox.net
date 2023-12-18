import time
import json
import traceback
import random
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

# Generate suggestion text inside of input box
def generateSuggestion(): 
    template_artists = ['JPEGMAFIA','Lorde','Johnny Cash','Steely Dan','The Strokes','Grimes','Fleetwood Mac',
                        'Oasis','Freddy Gibbs','Unknown Mortal Orchestra','The Weeknd','Paul McCartney'
                        'The Tragically Hip','Nickelback','Tame Impala','King Gizzard and the Lizard Wizard'
                        'BROCKHAMPTON','Queen','Mac DeMarco']
    template_sentences = ['more like','featuring','sounds like','vibe of','produced like','like','written by']

    random_sentence = random.choice(template_sentences)
    random_artist = random.choice(template_artists)

    return f'{random_sentence} {random_artist}'.lower()

suggestion = generateSuggestion()

app = Flask(__name__)

def run_gpt(question):
    ''' Synchronous Run for GPT4 Assistant Response for Question '''

    # Debug
    print("RUNNING GPT")
    print("QUESTION: " + question)

    # Create Message Object
    message = client.beta.threads.messages.create(thread_id=thread.id,role="user",content=question,)

    # Begin Synchronous Run 
    run = client.beta.threads.runs.create(thread_id=thread.id,assistant_id=assistant_id,)
    run = wait_on_run(run, client, thread)

    # Parse Response
    latest_message_object = client.beta.threads.messages.list(thread_id=thread.id,)
    print(latest_message_object) # DEBUG
    message_string = latest_message_object.data[0].content[0].text.value
    print("message_string: " + message_string) #DEBUG

    # Return Response
    try:
        message_parsed = json.loads(message_string)
        print("ANSWER: " + str(message_parsed)) # DEBUG
        return message_parsed
    except ValueError: #includes json.decoder.JSONDecodeError
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
    global suggestion
    ''' /index Route'''

    # Definitions
    question = ''
    answer = placeholder_response
    suggetion = suggestion
    
    if request.method in ['GET']:
        pass

    # If run_gpt conditions are met
    if request.method in ['POST']:
        if(request.form.get('question','').strip() in ''):
            question = suggestion
        else:
            question = request.form.to_dict().get('question')

        #run_gpt with question
        answer = run_gpt(question)

        #Generate has new suggestion (old one is either used or has already been seen)
        suggestion = generateSuggestion()

    #Render index.html
    return render_template("index.html", question=question, answer=answer, placeholder_response=placeholder_response, suggestion=suggestion)

@app.errorhandler(404)
def page_not_found(error):
    ''' 404 Error Handler '''
    return 'This page does not exist', 404

if __name__ == "__main__":
    app.run(debug=True, port=5001)
