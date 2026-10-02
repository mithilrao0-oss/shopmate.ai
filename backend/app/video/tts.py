"""
Text-to-speech using pyttsx3 (local, offline TTS engine).

Outputs WAV files. Works on Windows, macOS, and Linux.
"""

import io
import tempfile
from pathlib import Path

import pyttsx3


class TextToSpeech:
    def __init__(self, rate=140):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)  # words per minute

    def synthesize(self, text: str) -> bytes:
        """
        Synthesize text to audio and return WAV bytes.
        """

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name

        try:
            self.engine.save_to_file(text, temp_path)
            self.engine.runAndWait()

            with open(temp_path, "rb") as f:
                wav_bytes = f.read()

            return wav_bytes
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def synthesize_to_file(self, text: str, output_path: str) -> str:
        """
        Synthesize text to a WAV file and return the path.
        """

        self.engine.save_to_file(text, output_path)
        self.engine.runAndWait()
        return output_path
