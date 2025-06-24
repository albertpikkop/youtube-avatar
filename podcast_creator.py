import pyttsx3
from pydub import AudioSegment
import os


def text_to_speech(text, filename, voice=None, rate=150):
    """Convert text to speech and save as an audio file."""
    engine = pyttsx3.init()
    if voice is not None:
        engine.setProperty('voice', voice)
    engine.setProperty('rate', rate)
    engine.save_to_file(text, filename)
    engine.runAndWait()


def create_podcast(conversation_lines, output_file="podcast.mp3"):
    """Given a list of conversation lines, generate a podcast-style audio."""
    audio_segments = []
    temp_files = []
    for idx, line in enumerate(conversation_lines):
        temp_name = f"segment_{idx}.wav"
        text_to_speech(line, temp_name)
        audio_segments.append(AudioSegment.from_file(temp_name))
        temp_files.append(temp_name)
    if not audio_segments:
        raise ValueError("No conversation lines provided")
    podcast = audio_segments[0]
    for seg in audio_segments[1:]:
        podcast += seg
    podcast.export(output_file, format="mp3")
    for f in temp_files:
        os.remove(f)
    return output_file


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create podcast audio from conversation text.")
    parser.add_argument("input", help="Path to text file with conversation lines.")
    parser.add_argument("--output", default="podcast.mp3", help="Output audio file name.")
    args = parser.parse_args()

    with open(args.input, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    out = create_podcast(lines, args.output)
    print(f"Podcast saved to {out}")
