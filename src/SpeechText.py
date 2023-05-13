import whisper

class Whisper:
  model: whisper.Whisper
  
  def __init__(self, model_size='base') -> None:
    self.model = whisper.load_model(model_size)
  
  def transcribe(self, audio) -> str:
    text = self.model.transcribe(audio, fp16=False)['text']
    if not text:
      raise Exception("Could not transcribe audio.")
    return text