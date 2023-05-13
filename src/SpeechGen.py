import io
from gtts import gTTS

class TTS:
  tts: gTTS = gTTS
  
  @staticmethod
  def synthesize(text) -> io.BytesIO:
    tts = gTTS(text, lang='en')
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)  # Reset the file pointer to the beginning
    return audio_buffer