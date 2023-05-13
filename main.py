import warnings
from numba.core.errors import NumbaDeprecationWarning
# i don't give a hoot
warnings.simplefilter('ignore', category=NumbaDeprecationWarning)

from src.GUI import GPTFren

if __name__ == "__main__":
  try:
    GPTFren().run()
  except KeyboardInterrupt:
    print("Exiting...")
    # Save the HyperDB instance to a file
    # db.save("data/memory.pickle.gz")

# from uuid import uuid4

# Load environment variables
# load_dotenv()
# WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE") or "tiny"
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# GPT_MODEL= os.getenv("GPT_MODEL") or "gpt-3.5-turbo"
# MIC_INDEX = os.getenv("MIC_INDEX")
# ACTIVATION_KEY = os.getenv("ACTIVATION_KEY") or "f10"
# SHORT_MEMORY_LINES = os.getenv("SHORT_MEMORY_LINES") or 5
# LONG_MEMORY_LINES = os.getenv("LONG_MEMORY_LINES") or 5
# SEED_FILE = os.getenv("SEED_FILE") or "data/seed.jsonl"

# # Query the HyperDB instance with a text input
# if __name__ == "__main__":
#     try:
#       # Load whisper model
#       model = whisper.load_model(WHISPER_MODEL_SIZE or "base")
#       devices = list_audio_devices()
#       device_index = select_microphone(devices)
    
#       while True:
#         filepath = f"temp\\{str(uuid4())}.wav"
#         audio_data = record_audio(device_index)
#         write_audio_to_file(audio_data, filepath)
#         transcribed_text = model.transcribe(filepath, fp16=False)['text']
#         os.remove(filepath)
#         print(f"Transcribed text: {transcribed_text}")

#         if transcribed_text:
#             chatgpt_response = send_to_chatgpt(transcribed_text)
#             print(f"ChatGPT response: {chatgpt_response}")
#             if chatgpt_response:
#                 audio_file = synthesize_speech(chatgpt_response)
#                 play_audio_data(audio_file)
#                 if db is None:
#                     db = HyperDB()
#                 db.add_document(f"Query: {transcribed_text}\n\tResponse: {chatgpt_response}\n\n")
#                 short_memory.append({
#                   "user": transcribed_text,
#                   "assistant": chatgpt_response
#                 })
#                 short_memory = short_memory[-int(SHORT_MEMORY_LINES):]
#         else:
#             print("Could not transcribe audio.")
