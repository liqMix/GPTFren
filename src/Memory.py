import os
import json
from hyperdb import HyperDB

class Memory:
  SHORT_MEMORY_LIMIT: int = 5
  LONG_MEMORY_LIMIT: int = 5
  db: HyperDB = None
  history = []
  short_memory = []

  def __init__(self, file=None) -> None:
    if file and os.path.exists(file):
      self.db = HyperDB()
      self.db.load(file)
       
  def add_from_seed(self, file):
    if os.path.exists(file):
      with open(file, 'r') as f:
          for line in f:
            self.db.add_document(json.loads(line))
  
  def add_to_memory(self, prompt, response):
    self._add_to_long_memory(prompt, response)
    self._add_to_short_memory(prompt, response)

  def _add_to_long_memory(self, prompt, response):
    memory = f'Query: {prompt}\n\tResponse: {response}\n\n'
    if not self.db:
      self.db = HyperDB()
    self.db.add_document(memory)

  def _add_to_short_memory(self, prompt, response):
    memory = f'User: {prompt}\nAssistant: {response}\n'
    self.short_memory.append(memory)
    self.history.append(memory)
    if len(self.short_memory) > self.SHORT_MEMORY_LIMIT:
      self.short_memory.pop(0)
  
  def get_from_long_memory(self, query):
    if self.db:
      self.db.query(query)[:int(self.LONG_MEMORY_LIMIT)]
    else:
      return ''  
  
  def get_from_short_memory(self):
    return '\n'.join(self.short_memory)
  
  def get_history(self):
    return '\n'.join(self.history)
