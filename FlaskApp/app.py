import time
import json
import random
import spotipy
import traceback
from ast import literal_eval
from flask import Flask, render_template, request, redirect
from openai import OpenAI
from spotipy.oauth2 import SpotifyOAuth

#Spotipy API Setup
SCOPE = "user-library-read"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPE))

# Query Docs: https://developer.spotify.com/documentation/web-api/reference/search
def search_spotify(search_artist,search_track):
    ''' Return Spotify Track ID for string inputs of artist and track '''

    print(f'SEARCH_SPOTIFY: Running "{search_artist}" and "{search_track}"') #DEBUG

    #Formatting Inputs and Query
    search_artist = search_artist.replace(' ','%20')
    search_track = search_track.replace(' ','%20')
    query = f'q=artist:{search_artist}%20track:{search_track}'
    #query = f'q=track%3A{search_track}%2520artist%3A{search_artist}&type=track' #ex: q=track%3ABack%2520To%2520The%2520Egg%2520artist%3APaul%2520McCartney
    print(f'SEARCH_SPOTIPY: {query=}') #DEBUG

    #Search Spotipy
    try:
        tracks = sp.search(q=query, limit=1, offset=0)['tracks']
        track_items = tracks['items'][0]
        track_id = track_items['id']
    except IndexError:
        print('SEARCH_SPOTIFY: ')
        track_id = ''

    print('query: ' + query)
    print('track_uri: ' + track_id)
    return track_id

# OpenAI API Setup
client = OpenAI(organization='org-1VoooiSLTr711Aax6i6A5nUT',)
thread = client.beta.threads.create()
assistant_id = "asst_UIGVVCM7oTG66Q5mHmNYcGoq"

def generate_suggestion():
    ''' Generate suggestion text inside for the input box '''
    template_artists = ['JPEGMAFIA','Lorde','Johnny Cash','Steely Dan','The Strokes','Grimes','Fleetwood Mac',
                        'Oasis','Freddie Gibbs','Unknown Mortal Orchestra','The Weeknd','Paul McCartney',
                        'The Tragically Hip','Nickelback','Tame Impala','King Gizzard and the Lizard Wizard',
                        'BROCKHAMPTON','Queen','Mac DeMarco']

    template_sentences = ['more like','featuring','sounds like','vibe of','produced like','like','written by',
                          'intro to','latest from','from the debut of','the best of','deepcuts of']

    random_sentence = random.choice(template_sentences)
    random_artist = random.choice(template_artists)

    return f'{random_sentence} {random_artist}'.lower()

# Python Dict Placeholder Response
placeholder_response = {
    0: {"artist": "Artist Name 1", "track": "Track Name 1"},
    1: {"artist": "Artist Name 2", "track": "Track Name 2"},
    2: {"artist": "Artist Name 3", "track": "Track Name 3"},
    3: {"artist": "Artist Name 4", "track": "Track Name 4"},
    4: {"artist": "Artist Name 5", "track": "Track Name 5"}
}

def run_gpt(question):
    ''' Synchronous Run for GPT-4 Assistant Response with Question '''

    # Debug
    print(f'RUN_GPT: {question=}')

    # Create Message Object
    message = client.beta.threads.messages.create(thread_id=thread.id,role="user",content=question,)

    # Begin Synchronous Run 
    run = client.beta.threads.runs.create(thread_id=thread.id,assistant_id=assistant_id,)
    run = wait_on_run(run, client, thread)

    # Parse Response
    latest_message_object = client.beta.threads.messages.list(thread_id=thread.id,)
    response_value = latest_message_object.data[0].content[0].text.value

    # Return Response (will return placeholder_string if cannot parse input into dict)
    return text_to_dict(response_value)

def text_to_dict(input_string):
    ''' Takes String and safely converts to python dict, else placeholder_response '''
    if isinstance(input_string, dict):
        print('TEXT_TO_DICT: Already type dict!')
        return input_string
    elif not isinstance(input_string, str):
        print('TEXT_TO_DICT: Input not type string or dict!')
        return placeholder_response

    #Debug
    print(f'{input_string=}')
    print(f'TYPE: {type(input_string)}')

    #Parse Valid String
    try:
        return literal_eval(input_string)
    except ValueError:
        print("FAILED! placeholder_response used!") # DEBUG
        return placeholder_response

def wait_on_run(run, client, thread):
    ''' Syncronous Run Helper Function ''' 
    while run.status in ['queued', 'in_progress']:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.15)
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

        #Get question from input field
        question = request.form.to_dict().get('question').strip()
        if question in '':
            question = current_suggestion

        #run_gpt with question
        answer = run_gpt(question)

        #Generate has new suggestion (old one is used or has already been seen)
        suggestion = generate_suggestion()

        #Answer to Python List
        answer = text_to_dict(answer)

        #Creating ids list which contains Spotify track ids if placeholder_response not used
        ids.clear()
        for i in range(0,5):
            print(f'{i=}')
            ids.append(
                search_spotify(answer[i]['artist'], answer[i]['track'])
            )
            time.sleep(.15)
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
