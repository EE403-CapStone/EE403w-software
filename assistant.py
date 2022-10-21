import os
from xdrlib import ConversionError
import openai
import dotenv

dotenv.load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


class convo:
  def __init__(self):
    self.conversation = ""

    
  def query(self,question):
    start_sequence = "\nAI:"
    restart_sequence = "\nHuman: "

    self.conversation += restart_sequence+question+'\n'

    response = openai.Completion.create(
      model="text-davinci-002",
      prompt=self.conversation,
      temperature=0.9,
      max_tokens=250,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0.6,
      stop=["AI:","Human:"]
    )
    self.conversation += response.choices[0].text
    return response.choices[0].text
  
  
def test_prompt():
  response = openai.Completion.create(
  model="text-davinci-002",
  prompt="Say hi I'm mathilda",
  temperature=0.7,
  max_tokens=256,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0)
  return response.choices[0].text


