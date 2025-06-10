# LiveKit Telephony Demo

This repo contains a simple example showing how to bridge Twilio voice calls with LiveKit Cloud.
The demo uses:

- **Twilio** for inbound/outbound PSTN or VoIP calls.
- **LiveKit Cloud** to handle real-time audio streaming.
- **Deepgram** for speech-to-text (STT) and text-to-speech (TTS).
- **OpenAI GPT-4o Mini** as the language model to generate responses.

## Files

- `twiml_server.py` – Flask server that returns TwiML for Twilio. The TwiML connects the call to a LiveKit SIP domain.
- `livekit_demo.py` – Asynchronous script that dials a phone number and joins the corresponding LiveKit room. It transcribes speech with Deepgram, sends it to GPT‑4o Mini, converts the reply back to speech, and publishes it into the room.

## Usage

1. Set the required environment variables:
   ```bash
   export LIVEKIT_WS_URL=wss://your-livekit-url
   export LIVEKIT_TOKEN=your_livekit_token
   export LIVEKIT_SIP_DOMAIN=your-sip.livekit.cloud
   export TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   export TWILIO_AUTH_TOKEN=your_auth_token
   export TWILIO_FROM_NUMBER=+15551234567
   export TO_NUMBER=+15557654321
   export DEEPGRAM_API_KEY=dg_secret_key
   export OPENAI_API_KEY=sk-...
   ```

2. Start the TwiML server:
   ```bash
   python twiml_server.py
   ```

3. Run the demo script to place an outbound call and join the room:
   ```bash
   python livekit_demo.py
   ```

Twilio should be configured to send inbound calls to the `/twiml` endpoint of the server.
