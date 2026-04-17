import ElevenLabs 
from elevenlabs.client import ElevenLabs
from elevenlabs import stream
from elevenlabs.client import ElevenLabs

client = ElevenLabs()

audio_stream = client.text_to_speech.convert_as_stream(
    text="This is a test",
    voice_id="TRnaQb7q41oL7sV0w6Bu",
    model_id="eleven_multilingual_v2"
)

# option 1: play the streamed audio locally
stream(audio_stream)

# option 2: process the audio bytes manually
for chunk in audio_stream:
    if isinstance(chunk, bytes):
        print(chunk)

client = ElevenLabs(
  api_key='sk_3606701b5c7f809d7564b89f01fe41e9c465051acdf526c7',
)
