import time
import json
import random
import spotipy
import traceback
from flask import Flask, render_template, request, redirect
from openai import OpenAI
from spotipy.oauth2 import SpotifyOAuth

#Spotipy API Setup
SCOPE = "user-library-read"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPE))

# Query Docs: https://developer.spotify.com/documentation/web-api/reference/search
def search_spotify(search_artist,search_track):
    '''Search spotify given string inputs of artist and track'''

    print('running search!')
    #Formatting Inputs and Query
    search_artist = search_artist.replace(' ','%20')
    search_track = search_track.replace(' ' ,'%20')
    query = f'q=track:{search_track}%20artist:{search_artist}' #ex: q=track:Royals%20artist:Lorde

    #Search Spotipy
    tracks = sp.search(query, limit=1, offset=0)['tracks']
    track_items = tracks['items'][0]
    track_id = track_items['id']

    print('query: ' + query)
    print('track_uri: ' + track_id)
    return track_id

# OpenAI API Setup
client = OpenAI(organization='org-1VoooiSLTr711Aax6i6A5nUT',)
thread = client.beta.threads.create()
assistant_id = "asst_Z8EJORrugfSAMUgxKXWNAaXw"

def generate_suggestion():
    ''' Generate suggestion text inside for the input box '''
    template_artists = ['JPEGMAFIA','Lorde','Johnny Cash','Steely Dan','The Strokes','Grimes','Fleetwood Mac',
                        'Oasis','Freddy Gibbs','Unknown Mortal Orchestra','The Weeknd','Paul McCartney',
                        'The Tragically Hip','Nickelback','Tame Impala','King Gizzard and the Lizard Wizard',
                        'BROCKHAMPTON','Queen','Mac DeMarco']

    template_sentences = ['more like','featuring','sounds like','vibe of','produced like','like','written by',
                          'intro to','latest from','from the debut of','best of']

    random_sentence = random.choice(template_sentences)
    random_artist = random.choice(template_artists)

    return f'{random_sentence} {random_artist}'.lower()

# JSON Placeholder Response
placeholder_response = {'1': {'artist': '', 'track': ''},
                        '2': {'artist': '', 'track': ''},
                        '3': {'artist': '', 'track': ''},
                        '4': {'artist': '', 'track': ''},
                        '5': {'artist': '', 'track': ''}}

def run_gpt(question):
    ''' Synchronous Run for GPT-4 Assistant Response with Question '''

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
    message_string = latest_message_object.data[0].content[0].text.value

    #DEBUG print(latest_message_object)
    #DEBUG print("message_string: " + message_string)

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
    while run.status in ['queued', 'in_progress']:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.4)
    return run

# Generate First Suggestion
suggestion = generate_suggestion()

# Create Flask Obj
app = Flask(__name__)

@app.route('/', methods = ['POST','GET'])
def index():
    ''' /index Route'''
    global suggestion

    # Definitions
    question = ''
    answer = placeholder_response
    current_suggestion = suggestion
    ids = []

    if request.method in ['GET'] and request.method not in ['POST']:
        suggestion = generate_suggestion()

    # If run_gpt conditions are met
    if request.method in ['POST']:
        question = request.form.to_dict().get('question').strip()
        if question in '':
            question = current_suggestion

        #run_gpt with question
        answer = run_gpt(question)

        #Generate has new suggestion (old one is used or has already been seen)
        suggestion = generate_suggestion()

        #Creating ids list which contains Spotify track ids
        ids.clear()

        for i in range(1,6):
            print(i)
            ids.append(
                search_spotify(answer[str(i)]['artist'], answer[str(i)]['track'])
              )
            time.sleep(.5)
        print(ids) #DEBUG

    #Render index.html
    return render_template("index.html", question=question, answer=answer,
                                         placeholder_response=placeholder_response,
                                         suggestion=suggestion, ids = ids)

@app.errorhandler(404)
def page_not_found(error):
    ''' 404 Error Handler '''
    return redirect('/', code=302)
    #return 'This page does not exist', 404

if __name__ == "__main__":
    app.run(debug=True, port=5001)
