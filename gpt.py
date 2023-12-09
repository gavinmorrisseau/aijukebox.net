from openai import OpenAI
client = OpenAI()
response = input("[*]: ")
completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are the incredibly helpful cool robot chaz. Chaz, for short. Your purpose is to recommend songs based upon user inputs"},
    {"role": "user", "content": response}
  ]
)
print(completion.choices[0].message)