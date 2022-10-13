import os
import openai
import dotenv

dotenv.load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

response = openai.Completion.create(
  model="text-davinci-002",
  prompt="Say hi as a test",
  temperature=0.7,
  max_tokens=256,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0
)


class convo:
  def __init__(self):
    self.conversation = []
    
  def query(self,question):
    self.conversation.append(question)

    return question
  
  def test(self):
    response = openai.Completion.create(
    model="text-davinci-002",
    prompt="Hello say hi mathilda",
    temperature=0.7,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0)
    return response.choices[0].text
