import os
import json
from flask import Flask, request, render_template, send_file
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Record, Say

load_dotenv()
app = Flask(__name__)

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        to_number = request.form['phone']
        call = client.calls.create(
            url='https://hr-je85.onrender.com/voice?q=0',
            to=to_number,
            from_=TWILIO_PHONE_NUMBER
        )
        return f"✅ Call initiated! Call SID: {call.sid}"
    return render_template('index.html')

@app.route('/voice', methods=['GET', 'POST'])
def voice():
    q = int(request.args.get("q", 0))

    with open("questions.json") as f:
        questions = json.load(f)

    response = VoiceResponse()

    # If it's a recording callback
    if request.method == "POST":
        recording_url = request.values.get("RecordingUrl", "")
        if recording_url and q > 0:
            with open("recordings.txt", "a") as f:
                f.write(f"Q{q}: {questions[q-1]}\nRecording: {recording_url}.mp3\n\n")

    if q < len(questions):
        response.say(questions[q])
        response.record(
            action=f"/voice?q={q+1}",
            method="POST",
            max_length=15,
            timeout=5,
            play_beep=True
        )
    else:
        response.say("Thank you. We have recorded your responses. Goodbye!")
        response.hangup()

    return str(response)

@app.route('/download')
def download():
    return send_file("recordings.txt", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
