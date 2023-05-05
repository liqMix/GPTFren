# GPTFren

A lil` chat friend you can press a key and talk to and it will respond.
Holds a memory of short-term conversation and long-term conversation using [HyperDB](https://github.com/jdagdelen/hyperDB)

## Requirements

- Python
- OpenAI API Key

## Install

Recommend to create a venv for this

- Create venv: `python -m venv venv`
- Activate venv:
  - Windows: `venv/Scripts/Activate`
  - Linux: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements`

## Usage

Create an .env file and set your OpenAI API key.

Run `python main.py`

Select your microphone

Hold the activation key (default: `F10`) to record your speech, release when done.

## TODO

Better TTS
