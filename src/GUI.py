import asyncio
import threading
import time
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.core.window import Window

from src.Controller import Controller

class GPTFren(App):
  history: TextInput
  message: TextInput
  send_text_button: Button
  record_button: Button
  record_key_pressed: bool = False
  recording: bool = False

  def build(self):
    Window.clearcolor = (0, 0, 0, 1)  # set background color to black
    layout = GridLayout(cols=2, row_default_height=40, spacing=10, padding=10)

    layout.add_widget(Label(text='Instruction Prompt:', color=(1, 1, 1, 1)))  # white text
    instruction_input = TextInput(text=Controller.get_instructions(), height=500)
    instruction_input.bind(text=lambda _, text: Controller.set_instructions(text))
    layout.add_widget(instruction_input)

    layout.add_widget(Label(text='Audio Devices:', color=(1, 1, 1, 1)))  # white text
    device_select = Spinner(text=Controller.get_selected_audio_device(), values=Controller.get_audio_device_names())
    device_select.bind(text=lambda _, text: Controller.select_audio_device(text))
    layout.add_widget(device_select)

    layout.add_widget(Label(text='Message:', color=(1, 1, 1, 1)))  # white text
    self.message = TextInput(multiline=True)
    layout.add_widget(self.message)

    layout.add_widget(Label(text='History:', color=(1, 1, 1, 1)))  # white text
    self.history = TextInput(text=Controller.get_chat_history(), multiline=True)
    layout.add_widget(self.history)

    self.send_text_button = Button(text='Send Text')
    self.send_text_button.bind(on_release=lambda _: self.send_text(self.message.text))
    layout.add_widget(self.send_text_button)

    self.record_button = Button(text='Record')
    self.record_button.bind(on_press=lambda _: self.record())
    layout.add_widget(self.record_button)

    _thread = threading.Thread(target=asyncio.run, args=(self._check_keyboard_input(),))
    _thread.start()

    return layout

  def refresh_history(self):
    self.history.text = Controller.get_chat_history()

  def send_text(self, text):
    if not text:
      return
    self.send_text_button.disabled = True
    Controller.send_text(text)
    self.message.text = ""
    self.refresh_history()
    self.send_text_button.disabled = False

  def _is_recording(self):
    return self.record_button.state == 'down' or self.record_key_pressed
  
  async def _record(self):
    while self._is_recording():
      Controller.record()
    Controller.stop_recording()
    Clock.schedule_once(lambda _: self.refresh_history(), 0.5)
  
  def record(self):
    _thread = threading.Thread(target=asyncio.run, args=(self._record(),))
    _thread.start()
    self.refresh_history()
  
  async def _check_keyboard_input(self):
    while True:
      if Controller.is_record_key_pressed() and not self.record_key_pressed:
        self.record_key_pressed = True
        self.record()
      elif self.record_key_pressed:
        self.record_key_pressed = False
      else:
        time.sleep(0.5)
