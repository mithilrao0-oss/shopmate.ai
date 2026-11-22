"""
Text-to-speech using pyttsx3 (local, offline TTS engine).

Writes WAV files and reports how long each one is, so the renderer can time
every scene to its own voiceover.
"""

import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path

import pyttsx3


@dataclass
class SceneAudio:
    """The voiceover of one scene: a WAV file (None if the scene is silent) and its length."""

    path: str | None
    duration: float


def wav_duration(path: str) -> float:
    """Length of an audio file in seconds."""

    try:
        with wave.open(path, "rb") as wav_file:
            return wav_file.getnframes() / float(wav_file.getframerate())
    except (wave.Error, EOFError):
        pass

    # Not a plain PCM WAV; ask ffprobe (installed together with FFmpeg).
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "csv=p=0",
                path,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return float(result.stdout.strip())
    except (OSError, subprocess.SubprocessError, ValueError):
        return 0.0


class TextToSpeech:
    def __init__(self, rate=140):
        self.rate = rate  # words per minute

    def _save_all(self, jobs: list[tuple[str, str]]) -> None:
        """
        Write several (text, wav_path) jobs with ONE engine and ONE runAndWait().

        pyttsx3 on Windows can hang or go silent when runAndWait() is called
        again and again, so all jobs are queued first and run together.
        """

        engine = pyttsx3.init()

        try:
            engine.setProperty("rate", self.rate)

            for text, path in jobs:
                engine.save_to_file(text, path)

            engine.runAndWait()
        finally:
            try:
                engine.stop()
            except Exception:
                pass

    @staticmethod
    def _check_written(path: str) -> None:
        file = Path(path)

        # A valid WAV is at least a 44-byte header.
        if not file.exists() or file.stat().st_size <= 44:
            raise RuntimeError(f"Text-to-speech produced no audio for {path}")

    def synthesize_to_file(self, text: str, output_path: str) -> str:
        """
        Synthesize text to a WAV file and return the path.
        """

        self._save_all([(text, output_path)])
        self._check_written(output_path)

        return output_path

    def synthesize(self, text: str) -> bytes:
        """
        Synthesize text to audio and return WAV bytes.
        """

        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name

        try:
            self.synthesize_to_file(text, temp_path)

            with open(temp_path, "rb") as f:
                return f.read()
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def synthesize_scenes(
        self,
        texts: list[str],
        out_dir: str,
        prefix: str = "scene",
    ) -> list[SceneAudio]:
        """
        Speak each scene separately. Returns one SceneAudio per input text,
        in the same order. Blank text gives a silent scene (path None).
        """

        out_directory = Path(out_dir)
        out_directory.mkdir(parents=True, exist_ok=True)

        jobs = []
        paths: list[str | None] = []

        for index, text in enumerate(texts):
            if text and text.strip():
                path = str(out_directory / f"{prefix}_{index}.wav")
                jobs.append((text.strip(), path))
                paths.append(path)
            else:
                paths.append(None)

        if jobs:
            self._save_all(jobs)

        scene_audio = []

        for path in paths:
            if path is None:
                scene_audio.append(SceneAudio(path=None, duration=0.0))
                continue

            self._check_written(path)
            scene_audio.append(SceneAudio(path=path, duration=wav_duration(path)))

        return scene_audio
