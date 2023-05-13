import os
import threading
import asyncio
import keyboard

from dotenv import load_dotenv
from uuid import uuid4
from src.Audio import Audio
from src.Memory import Memory
from src.SpeechText import Whisper
from src.TextGen import ChatGPT
from src.SpeechGen import TTS
from src.Prompt import Prompt
# Controller
# Responsible for coordinating user input and the generation classes
# to produce the final output.

class Controller:
  load_dotenv()

  WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE") or "tiny"
  OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
  GPT_MODEL= os.getenv("GPT_MODEL") or "gpt-3.5-turbo"
  MIC_INDEX = os.getenv("MIC_INDEX")
  ACTIVATION_KEY = os.getenv("ACTIVATION_KEY") or "f10"
  SHORT_MEMORY_LINES = os.getenv("SHORT_MEMORY_LINES") or 5
  LONG_MEMORY_LINES = os.getenv("LONG_MEMORY_LINES") or 5
  SEED_FILE = os.getenv("SEED_FILE") or "data/seed.jsonl"

  Audio = Audio()
  Memory = Memory()
  SpeechText = Whisper(WHISPER_MODEL_SIZE)
  TextGen = ChatGPT(OPENAI_API_KEY, GPT_MODEL)
  SpeechGen = TTS()
  Prompt = Prompt()

  recording: bool = False
  enable_speech: bool = True

  ## Prompt
  @staticmethod
  def get_instructions():
    return Controller.Prompt.get_instructions()
  
  @staticmethod
  def set_instructions(text):
    return Controller.Prompt.set_instructions(text)
  
  ## Text Input
  @staticmethod
  def send_text(text):
    long = Controller.Memory.get_from_long_memory(text)
    short = Controller.Memory.get_from_short_memory()
    prompt = Controller.Prompt.construct_prompt(text, long, short)
    response = Controller.TextGen.get_response(prompt)
    Controller.Memory.add_to_memory(text, response)
    if Controller.enable_speech:
      tts = Controller.SpeechGen.synthesize(response)
      _thread = threading.Thread(target=asyncio.run, args=(Controller.Audio.play_audio_file(tts),))
      _thread.start()


  ## Audio
  @staticmethod
  def get_audio_device_names():
    return map(lambda x: x['name'], Controller.Audio.get_devices())

  @staticmethod
  def select_audio_device(name):
    return Controller.Audio.select_device_by_name(name)
  
  @staticmethod
  def get_selected_audio_device():
    return Controller.Audio.get_selected_device()

  @staticmethod
  def is_record_key_pressed():
    return keyboard.is_pressed(Controller.ACTIVATION_KEY)

  @staticmethod
  def record():
    Controller.Audio.record()
  
  @staticmethod
  def stop_recording():
    filepath = f"temp\\{str(uuid4())}.wav"
    audio_data = Controller.Audio.get_recording()
    Controller.Audio.write_audio_to_file(audio_data, filepath)
    text = Controller.SpeechText.transcribe(filepath)
    os.remove(filepath)
    Controller.send_text(text)
  
  @staticmethod
  def get_chat_history():
    return Controller.Memory.get_history()