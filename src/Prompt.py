            

class Prompt:
  instructions = """You are a helpful assistant. You answer briefly and succinctly."""
  username: str = None

  def get_instructions(self):
    print(self.instructions)
    return self.instructions
  
  def set_instructions(self, instructions):
    self.instructions = instructions
    print(self.instructions)
  
  def construct_prompt(self, message, long_memory, short_memory):
    return f"""
      {self.instructions}
      {"You are talking with " + self.username if self.username else ""}
      Relative context:
        {long_memory}
      Previous conversation:
        {short_memory}

      {message}
    """