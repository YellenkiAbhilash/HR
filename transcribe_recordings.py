import os
from faster_whisper import WhisperModel

# Load the Whisper model (choose: "tiny", "base", "small", "medium", "large")
model = WhisperModel("base", compute_type="int8")  # "int8" works well on CPU

# Directory containing recorded mp3 files
recordings_dir = "recordings"
output_file = "responses.txt"

# Ensure output file is clean before writing
with open(output_file, "w", encoding="utf-8") as out_f:
    # Process each audio file
    for file_name in sorted(os.listdir(recordings_dir)):
        if file_name.endswith(".mp3"):
            audio_path = os.path.join(recordings_dir, file_name)
            print(f"🔍 Transcribing: {audio_path}")

            segments, _ = model.transcribe(audio_path)
            
            out_f.write(f"File: {file_name}\n")
            for segment in segments:
                out_f.write(f"{segment.text.strip()}\n")
            out_f.write("\n")

print(f"✅ Transcription completed. Saved to: {output_file}")
