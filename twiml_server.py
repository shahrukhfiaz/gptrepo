from flask import Flask, request, Response
import os

LIVEKIT_SIP_DOMAIN = os.getenv("LIVEKIT_SIP_DOMAIN")

a = Flask(__name__)

@a.route('/twiml', methods=['GET', 'POST'])
def twiml():
    room = request.args.get('room')
    token = request.args.get('token')
    response = f"""<?xml version='1.0' encoding='UTF-8'?>
<Response>
  <Dial>
    <Sip>sip:{room}@{LIVEKIT_SIP_DOMAIN}?X-LK-TOKEN={token}</Sip>
  </Dial>
</Response>"""
    return Response(response, mimetype='text/xml')

if __name__ == '__main__':
    a.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
