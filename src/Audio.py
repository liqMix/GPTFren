import pyaudio
import wave
from pydub import AudioSegment
from pydub.utils import make_chunks

class Audio:
  pyaudio: pyaudio.PyAudio
  mic_index: int
  devices: list
  selected_device: dict

  # Audio Details
  rate: int = 16000
  chunk_size: int = 1024
  format: int = pyaudio.paInt32

  # Audio Stream
  stream: pyaudio.Stream = None
  frames = []

  def __init__(self, mic_index=3) -> None:
    self.mic_index = mic_index
    self.devices = []
    self.pyaudio = pyaudio.PyAudio()
    self._refresh_devices()
    self.select_device(self.mic_index)
  
  def _refresh_devices(self):
    device_count = self.pyaudio.get_device_count()
    for i in range(device_count):
      device_info = self.pyaudio.get_device_info_by_index(i)
      if device_info['maxInputChannels'] > 0:
        self.devices.append(device_info)

  def get_devices(self):
    return self.devices

  def get_device_names(self): 
    return [device['name'] for device in self.devices]

  def select_device(self, idx):
    self.mic_index = idx
    self.selected_device = self.devices[idx]
    print(f"Selected device: {self.selected_device['name']}, index: {self.mic_index}")
    self._open_stream()

  def select_device_by_name(self, name):
    idx = self.get_device_names().index(name)
    self.select_device(idx)

  def get_selected_device(self):
    return self.selected_device['name']

  def _open_stream(self):
    if not self.selected_device:
      raise Exception("No microphone selected.")
    
    if self.stream:
      self.stream.stop_stream()
      self.stream.close()
    
    channels = int(self.selected_device['maxInputChannels'])
    self.stream = self.pyaudio.open(
      format=self.format, 
      rate=self.rate,
      channels=channels, 
      input=True, 
      frames_per_buffer=self.chunk_size, 
      input_device_index=self.mic_index
    )

  def set_activation_key(self, key):
    self.activation_key = key

  def record(self):
    data = self.stream.read(self.chunk_size)
    self.frames.append(data)

  def get_recording(self):
    audio_data = b''.join(self.frames)
    self.frames = []
    return audio_data
  
  async def play_audio_file(self, audio_file):
      audio_segment = AudioSegment.from_file(audio_file, format="mp3")
      stream = self.pyaudio.open(
         format=self.pyaudio.get_format_from_width(audio_segment.sample_width),
        channels=audio_segment.channels,
        rate=audio_segment.frame_rate,
        output=True
      )

      chunks = make_chunks(audio_segment, self.chunk_size)

      for chunk in chunks:
          audio_data = chunk._data
          stream.write(audio_data)

      stream.stop_stream()
      stream.close()

  def write_audio_to_file(self, audio_data, filepath, channels=1):
    with wave.open(filepath, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(self.pyaudio.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(audio_data)
