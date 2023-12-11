import time
import json
import sys
from openai import OpenAI

# ~ Docs ~
# https://cookbook.openai.com/examples/assistants_api_overview_python
# https://platform.openai.com/docs/assistants/how-it-works/managing-threads-and-messages

def wait_on_run(run, thread):
  while run.status == "queued" or run.status == "in_progress":
      run = client.beta.threads.runs.retrieve(
          thread_id=thread.id,
          run_id=run.id,
      )
      time.sleep(0.5)
  return run

client = OpenAI(
  organization='org-1VoooiSLTr711Aax6i6A5nUT',
)

thread = client.beta.threads.create()
PROMPT = input("[*]: ").lower().strip() or "Give me a list of 5 random great songs"
ASSISTANT_ID = "asst_Z8EJORrugfSAMUgxKXWNAaXw"

message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=PROMPT,
)

run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=ASSISTANT_ID,
)

run = wait_on_run(run, thread)
messages = client.beta.threads.messages.list(thread_id=thread.id)
message_object = messages.data[0].content[0].text.value

try:
    message_parsed = json.loads(message_object)
except json.decoder.JSONDecodeError:
    print(f'FAILED: \n{message}')
    sys.exit()

for count in range(1,6):
    artist = str(message_parsed[str(count)]['artist'])
    track = str(message_parsed[str(count)]['track'])
    print(f'{track} by {artist}')
