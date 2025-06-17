import os
import json
from flask import Flask, request, render_template
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather

load_dotenv()
app = Flask(__name__)

# Load Twilio credentials from environment
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        to_number = request.form['phone']
        call = client.calls.create(
            url='https://hr-je85.onrender.com/voice?q=0',  # Your deployed URL
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

    # Record answer from last question
    if request.method == "POST":
        answer = request.values.get("SpeechResult", "").strip()
        if answer and q > 0:
            with open("responses.txt", "a") as f:
                f.write(f"Q{q}: {questions[q-1]}\nA: {answer}\n\n")

    if q < len(questions):
        gather = Gather(input='speech', action=f"/voice?q={q+1}", method="POST", timeout=5)
        gather.say(questions[q])
        response.append(gather)
        response.redirect(f"/voice?q={q}")  # If no speech input, repeat the question
    else:
        response.say("Thank you. We have recorded your responses. Goodbye!")
        response.hangup()

    return str(response)

if __name__ == '__main__':
    app.run(debug=True)
