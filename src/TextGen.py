import openai

class ChatGPT:
  model: str
  
  def __init__(self, api_key, model="gpt-3.5-turbo"):
    if not api_key:
      raise Exception("OpenAI API key must be provided in order to use ChatGPT.")
    openai.api_key = api_key
    self.model = model

  def get_response(self, prompt):
    completion = openai.ChatCompletion.create(
      model=self.model,
      messages=[
       {
          "role": "system",
          "content": prompt
        },
        {"role": "user", "content": prompt}
      ]
    )
    return completion.choices[0].message["content"]

