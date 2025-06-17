import os
import json
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///responses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define database model
class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500))
    answer = db.Column(db.String(1000))

# Load Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Route to show the homepage and trigger the call
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        to_number = request.form['phone']
        call = client.calls.create(
            url='https://hr-je85.onrender.com/voice?q=0',  # Change this to your deployed URL
            to=to_number,
            from_=TWILIO_PHONE_NUMBER
        )
        return f"✅ Call initiated! Call SID: {call.sid}"
    return render_template('index.html')

# Voice interaction endpoint
@app.route('/voice', methods=['GET', 'POST'])
def voice():
    q = int(request.args.get("q", 0))

    with open("questions.json") as f:
        questions = json.load(f)

    response = VoiceResponse()

    if request.method == "POST":
        answer = request.values.get("SpeechResult", "").strip()
        if answer and q > 0:
            # Save Q&A into the database
            entry = Response(question=questions[q-1], answer=answer)
            db.session.add(entry)
            db.session.commit()

    if q < len(questions):
        gather = Gather(input='speech', action=f"/voice?q={q+1}", method="POST", timeout=5)
        gather.say(questions[q])
        response.append(gather)
        response.redirect(f"/voice?q={q}")  # Repeat question if no speech
    else:
        response.say("Thank you. We have recorded your responses. Goodbye!")
        response.hangup()

    return str(response)

# Optional route to view all stored responses
@app.route('/responses')
def show_responses():
    responses = Response.query.all()
    return render_template('responses.html', responses=responses)

@app.route('/responses')
def show_responses():
    responses = Response.query.all()
    return render_template('responses.html', responses=responses)

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates tables if not exist
    app.run(debug=True)
