import io
import os
import pyaudio
import requests
import json
import wave
import whisper
import keyboard
from pydub import AudioSegment
from pydub.utils import make_chunks
from gtts import gTTS
from uuid import uuid4
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE")
CHATGPT_API_KEY = os.getenv("CHATGPT_API_KEY")
DEFAULT_MIC_INDEX = os.getenv("DEFAULT_MIC_INDEX")

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
    if(DEFAULT_MIC_INDEX != None):
      return int(DEFAULT_MIC_INDEX)
    print("Select the microphone to use:")
    for i, device_info in devices:
        print(f"{i}: {device_info['name']}")

    selected_index = int(input("Enter the index of the microphone: "))
    print("\nSelected microphone information:")
    print(json.dumps(devices[selected_index][1], indent=2))
    return devices[selected_index][0]
  
def record_audio(device_index, rate=16000, chunk_size=1024):
    audio = pyaudio.PyAudio()
    device_info = audio.get_device_info_by_index(device_index)
    channels = int(device_info['maxInputChannels'])

    stream = audio.open(format=pyaudio.paInt32, rate=rate, channels=channels, input=True, frames_per_buffer=chunk_size, input_device_index=device_index)

    print("Hold the spacebar to record audio, release to stop recording and send to Whisper.")
    frames = []

    while True:
        if keyboard.is_pressed('space'):
            print("Recording...", end="\r")
            data = stream.read(chunk_size)
            frames.append(data)
        elif frames:
            print("Stopped recording. Sending audio to Whisper...")
            break

    stream.stop_stream()
    stream.close()
    audio.terminate()

    audio_data = b''.join(frames)
    return audio_data

def send_to_chatgpt(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHATGPT_API_KEY}"
    }
    print(headers)
    url = "https://api.openai.com/v1/chat/completions"
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. You answer briefly and succinctly."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

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
      print(f"Using microphone {device_index}")
    
      while True:
        filepath = f"temp\\{str(uuid4())}.wav"
        audio_data = record_audio(device_index)
        write_audio_to_file(audio_data, filepath)
        transcribed_text = model.transcribe(filepath)['text']
        os.remove(filepath)
        print(f"Transcribed text: {transcribed_text}")

        if transcribed_text:
            chatgpt_response = send_to_chatgpt(transcribed_text)
            print(f"ChatGPT response: {chatgpt_response}")
            if chatgpt_response:
                audio_file = synthesize_speech(chatgpt_response)
                play_audio_data(audio_file)
        else:
            print("Could not transcribe audio.")
    except KeyboardInterrupt:
      print("Exiting...")