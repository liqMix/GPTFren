import warnings
from numba.core.errors import NumbaDeprecationWarning
# i don't give a hoot
warnings.simplefilter('ignore', category=NumbaDeprecationWarning)

import io
import keyboard
import openai
import os
import pyaudio
import wave
import whisper
from dotenv import load_dotenv
from gtts import gTTS
from hyperdb import HyperDB
from pydub import AudioSegment
from pydub.utils import make_chunks
from uuid import uuid4

# Load environment variables
load_dotenv()
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE") or "tiny"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GPT_MODEL= os.getenv("GPT_MODEL") or "gpt-3.5-turbo"
MIC_INDEX = os.getenv("MIC_INDEX")
ACTIVATION_KEY = os.getenv("ACTIVATION_KEY") or "f10"
SHORT_MEMORY_LINES = os.getenv("SHORT_MEMORY_LINES") or 5
LONG_MEMORY_LINES = os.getenv("LONG_MEMORY_LINES") or 5

if not OPENAI_API_KEY:
   raise Exception("OPENAI_API_KEY environment variable not set")
openai.api_key = OPENAI_API_KEY

# Load vector DB
# If no existing memory, delay creation until first document is available
db = None
if(os.path.exists("data/memory.pickle.gz")):
  db = HyperDB()
  db.load("data/memory.pickle.gz")

# Init short term memory
short_memory = []

# Query the HyperDB instance with a text input
def list_audio_devices():
    audio = pyaudio.PyAudio()
    device_count = audio.get_device_count()
    devices = []

    for i in range(device_count):
        device_info = audio.get_device_info_by_index(i)
        devices.append((i, device_info))

    audio.terminate()
    return devices

def select_microphone(devices):
    if(MIC_INDEX != None):
      idx = int(MIC_INDEX)
      print("Using default microphone: ", devices[idx][1]["name"])
      return idx
    
    print("Select the microphone to use:")
    for i, device_info in devices:
        print(f"{i}: {device_info['name']}")

    selected_index = int(input("Enter the index of the microphone: "))
    return devices[selected_index][0]
  
def record_audio(device_index, rate=16000, chunk_size=1024):
    audio = pyaudio.PyAudio()
    device_info = audio.get_device_info_by_index(device_index)
    channels = int(device_info['maxInputChannels'])

    stream = audio.open(format=pyaudio.paInt32, rate=rate, channels=channels, input=True, frames_per_buffer=chunk_size, input_device_index=device_index)

    print(f"\nHold down {str.upper(ACTIVATION_KEY)} to record audio, release to stop.")
    frames = []

    while True:
        if keyboard.is_pressed(ACTIVATION_KEY):
            print("Recording...", end="\r")
            data = stream.read(chunk_size)
            frames.append(data)
        elif frames:
            print("Processing...")
            break

    stream.stop_stream()
    stream.close()
    audio.terminate()

    audio_data = b''.join(frames)
    return audio_data

def get_prompt_memory(prompt):
    relative_context = ""
    if db:
        for doc in db.query(prompt)[:int(LONG_MEMORY_LINES)]:
            relative_context += doc[0]

    sm_string = ""
    for sm in short_memory:
         sm_string += f"{str(sm)}\n"
    
    return f"""
      Relative context:
        {relative_context}
      Previous conversation:
        {sm_string}
    """

def send_to_chatgpt(prompt):
    memory_string = get_prompt_memory(prompt)
    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
       {
          "role": "system",
          "content": f"""
            You are a helpful assistant. You answer briefly and succinctly.
            You use this context in order to respond:
            {memory_string}
          """
        },
        {"role": "user", "content": prompt}
      ]
    )
    return completion.choices[0].message["content"]

def write_audio_to_file(audio_data, filepath, channels=1, rate=16000):
    with wave.open(filepath, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt32))
        wf.setframerate(rate)
        wf.writeframes(audio_data)

def synthesize_speech(text):
    tts = gTTS(text, lang='en')
    audio_file = io.BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)  # Reset the file pointer to the beginning
    return audio_file

def play_audio_data(audio_file):
    audio_segment = AudioSegment.from_file(audio_file, format="mp3")
    audio = pyaudio.PyAudio()

    stream = audio.open(format=audio.get_format_from_width(audio_segment.sample_width),
                        channels=audio_segment.channels,
                        rate=audio_segment.frame_rate,
                        output=True)

    chunk_size = 1024
    chunks = make_chunks(audio_segment, chunk_size)

    for chunk in chunks:
        audio_data = chunk._data
        stream.write(audio_data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

if __name__ == "__main__":
    try:
      # Load whisper model
      model = whisper.load_model(WHISPER_MODEL_SIZE or "base")
      devices = list_audio_devices()
      device_index = select_microphone(devices)
    
      while True:
        filepath = f"temp\\{str(uuid4())}.wav"
        audio_data = record_audio(device_index)
        write_audio_to_file(audio_data, filepath)
        transcribed_text = model.transcribe(filepath, fp16=False)['text']
        os.remove(filepath)
        print(f"Transcribed text: {transcribed_text}")

        if transcribed_text:
            chatgpt_response = send_to_chatgpt(transcribed_text)
            print(f"ChatGPT response: {chatgpt_response}")
            if chatgpt_response:
                audio_file = synthesize_speech(chatgpt_response)
                play_audio_data(audio_file)
                if db is None:
                    db = HyperDB()
                db.add_document(f"Query: {transcribed_text}\n\tResponse: {chatgpt_response}\n\n")
                short_memory.append({
                  "user": transcribed_text,
                  "assistant": chatgpt_response
                })
                short_memory = short_memory[-int(SHORT_MEMORY_LINES):]
        else:
            print("Could not transcribe audio.")
    except KeyboardInterrupt:
      print("Exiting...")
      # Save the HyperDB instance to a file
      db.save("data/memory.pickle.gz")