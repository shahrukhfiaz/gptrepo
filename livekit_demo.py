import os
import asyncio
from typing import Optional

from twilio.rest import Client as TwilioClient
from deepgram import DeepgramClient, LiveOptions, SpeakOptions
import openai
from livekit.rtc import Room, RoomOptions

# Environment variables
LIVEKIT_WS_URL = os.getenv("LIVEKIT_WS_URL")
LIVEKIT_TOKEN = os.getenv("LIVEKIT_TOKEN")
LIVEKIT_SIP_DOMAIN = os.getenv("LIVEKIT_SIP_DOMAIN")  # e.g. 'myproject.telephony.livekit.cloud'
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
dg_client = DeepgramClient(api_key=DEEPGRAM_API_KEY)

async def transcribe_and_respond(room: Room):
    """Subscribe to audio tracks, send to Deepgram STT and reply using TTS."""
    async def on_track_subscribed(track, publication, participant):
        # Connect to Deepgram's streaming API
        options = LiveOptions(language="en-US", smart_format=True)
        dg_socket = dg_client.listen.v("1").websocket
        dg_conn = dg_socket.open(options=options)
        dg_conn.start()

        async def handle_dg_events():
            async for msg in dg_conn.results():
                if msg.channel and msg.channel.alternatives:
                    text = msg.channel.alternatives[0].transcript
                    if text:
                        print("User:", text)
                        resp = openai.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": text}]
                        )
                        reply = resp.choices[0].message.content
                        print("Assistant:", reply)
                        audio = dg_client.speak.v("1").rest.speak(
                            SpeakOptions(text=reply, model="aura-asteria")
                        )
                        room.local_participant.publish_audio_frame(audio.audio)
        asyncio.create_task(handle_dg_events())

        async for frame in track.frames():
            dg_conn.send(frame.data)

    room.on("track_subscribed", on_track_subscribed)

async def start_room() -> Room:
    room = Room()
    await room.connect(LIVEKIT_WS_URL, LIVEKIT_TOKEN, RoomOptions())
    await transcribe_and_respond(room)
    return room

def dial_twilio(room_name: str, token: str, to_number: str):
    url = f"https://YOUR_HOST/twiml?room={room_name}&token={token}"
    call = twilio_client.calls.create(to=to_number, from_=TWILIO_FROM_NUMBER, url=url)
    print("Started call:", call.sid)

if __name__ == "__main__":
    to = os.getenv("TO_NUMBER")
    room_name = os.getenv("LIVEKIT_ROOM", "demo-room")
    token = LIVEKIT_TOKEN
    dial_twilio(room_name, token, to)
    asyncio.run(start_room())
