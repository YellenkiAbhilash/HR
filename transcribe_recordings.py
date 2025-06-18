import whisper
import os
import requests

# Load Whisper model
model = whisper.load_model("base")  # Use "medium" or "large" for better accuracy

output = []

# Read recording URLs from file
with open("recordings.txt") as f:
    lines = f.readlines()

for i in range(0, len(lines), 3):
    question = lines[i].strip()
    url_line = lines[i+1].strip()
    url = url_line.split("Recording: ")[1]

    # Download recording
    filename = f"recording_{i//3 + 1}.mp3"
    r = requests.get(url)
    with open(filename, "wb") as audio:
        audio.write(r.content)

    # Transcribe
    result = model.transcribe(filename)
    text = result["text"].strip()

    output.append(f"{question}\nA: {text}\n\n")

# Save to responses.txt
with open("responses.txt", "w", encoding="utf-8") as f:
    f.writelines(output)

print("✅ Transcription complete. See responses.txt")
