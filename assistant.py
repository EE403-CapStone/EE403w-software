import os
import openai
import dotenv

dotenv.load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


class convo:
  def __init__(self):
    self.conversation = []
    
  def query(self,question):
    self.conversation.append(question)

    return question
  
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
