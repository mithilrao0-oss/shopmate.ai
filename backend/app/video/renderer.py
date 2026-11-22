"""
Video renderer: turn a reel script into a 9:16 MP4 with FFmpeg.

For every scene it
  1. takes the length of that scene's own voiceover,
  2. renders a clip of the product image with a slow zoom or pan that lasts
     exactly as long as the voiceover (plus a short pause),
then joins the clips and burns in the headline and the spoken captions.

No per-frame PNG files are written, so rendering is much faster and uses far
less disk than a frame-by-frame approach.
"""

import math
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


class VideoRenderer:
    """
    Render a reel script into an Instagram Reel (9:16).
    """

    # "final" is the full 1080x1920 reel. "preview" is a quick, smaller render
    # for checking a script before spending time on the final one.
    QUALITY = {
        "final": {"width": 1080, "height": 1920, "fps": 30, "crf": 23, "preset": "veryfast"},
        "preview": {"width": 720, "height": 1280, "fps": 24, "crf": 28, "preset": "ultrafast"},
    }

    # The background image is built at 1.5x the final size so zooming in stays sharp.
    SOURCE_WIDTH = 1620
    SOURCE_HEIGHT = 2880

    PAUSE_SECONDS = 0.4  # short pause after each scene's voiceover
    MIN_SCENE_SECONDS = 2.0  # even a one-word scene stays on screen this long

    # Slow camera moves, cycled scene by scene so the video does not feel static.
    ZOOM_AMOUNT = 0.15
    PAN_ZOOM = 1.18

    # Captions are positioned for a 1080x1920 canvas (libass scales them for
    # other sizes) and kept clear of the Instagram buttons and caption area.
    CAPTION_MAX_WORDS = 4

    ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,Arial,68,&H00FFFFFF,&H000000FF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,6,2,2,80,80,420,1
Style: Headline,Arial,84,&H0000D7FF,&H000000FF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,7,2,8,80,80,260,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="reel_")
        self.temp_path = Path(self.temp_dir)
        self.duration = 0.0  # length of the last rendered video, in seconds
        self.warnings: list[str] = []

    def cleanup(self):
        """Remove temporary files."""

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # ------------------------------------------------------------------
    # Background image
    # ------------------------------------------------------------------

    def _build_background(self, image_path: str, output_path: str) -> None:
        """
        Make a 9:16 background from the product image.

        A photo that is already close to 9:16 simply fills the frame. Any other
        photo is shown whole, in front of a blurred, dimmed copy of itself, so
        the product is never cropped.
        """

        width, height = self.SOURCE_WIDTH, self.SOURCE_HEIGHT

        try:
            image = Image.open(image_path).convert("RGB")
        except Exception:
            image = Image.new("RGB", (width, height), color=(30, 30, 30))

        aspect = image.width / image.height

        if abs(aspect - width / height) < 0.08:
            canvas = ImageOps.fit(image, (width, height), Image.Resampling.LANCZOS)
            canvas.save(output_path, quality=95)
            return

        # Blur a small copy (fast), then enlarge it as the backdrop.
        small = ImageOps.fit(
            image, (width // 4, height // 4), Image.Resampling.LANCZOS
        ).filter(ImageFilter.GaussianBlur(radius=12))

        backdrop = small.resize((width, height), Image.Resampling.BILINEAR)
        backdrop = ImageEnhance.Brightness(backdrop).enhance(0.55)

        product = ImageOps.contain(
            image, (width - 120, int(height * 0.62)), Image.Resampling.LANCZOS
        )

        left = (width - product.width) // 2
        top = int(height * 0.46 - product.height / 2)

        backdrop.paste(product, (left, top))
        backdrop.save(output_path, quality=95)

    # ------------------------------------------------------------------
    # One scene clip
    # ------------------------------------------------------------------

    def _motion(self, scene_index: int, frames: int) -> str:
        """zoompan expressions for this scene's camera move (no commas, so no quoting trouble)."""

        zoom = self.ZOOM_AMOUNT
        pan = self.PAN_ZOOM
        n = max(frames, 1)

        centre_x = "x='iw/2-(iw/zoom/2)'"
        centre_y = "y='ih/2-(ih/zoom/2)'"

        moves = [
            f"z='1+{zoom}*on/{n}':{centre_x}:{centre_y}",  # slow zoom in
            f"z='{pan}':x='(iw-iw/zoom)*on/{n}':{centre_y}",  # pan left to right
            f"z='1+{zoom}-{zoom}*on/{n}':{centre_x}:{centre_y}",  # slow zoom out
            f"z='{pan}':x='(iw-iw/zoom)*(1-on/{n})':{centre_y}",  # pan right to left
        ]

        return moves[scene_index % len(moves)]

    def _render_scene_clip(
        self,
        background: Path,
        audio_path: str | None,
        scene_seconds: float,
        scene_index: int,
        output_path: Path,
        quality: dict,
    ) -> None:
        width, height, fps = quality["width"], quality["height"], quality["fps"]
        frames = max(1, math.ceil(scene_seconds * fps))

        video_filter = (
            f"[0:v]zoompan={self._motion(scene_index, frames)}"
            f":d={frames}:s={width}x{height}:fps={fps},format=yuv420p[v]"
        )

        # apad stretches the audio to the full scene length (voiceover + pause).
        audio_filter = f"[1:a]aresample=44100,apad=whole_dur={scene_seconds:.3f}[a]"

        command = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(background)]

        if audio_path:
            command += ["-i", audio_path]
        else:
            command += ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]

        command += [
            "-filter_complex",
            f"{video_filter};{audio_filter}",
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-t",
            f"{scene_seconds:.3f}",
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-crf",
            "20",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-ac",
            "2",
            str(output_path),
        ]

        self._run(command, timeout=180)

    # ------------------------------------------------------------------
    # Captions (ASS subtitle file, burned in by FFmpeg)
    # ------------------------------------------------------------------

    @staticmethod
    def _ass_time(seconds: float) -> str:
        centiseconds = int(round(max(seconds, 0) * 100))

        hours = centiseconds // 360000
        minutes = (centiseconds // 6000) % 60
        secs = (centiseconds // 100) % 60
        cs = centiseconds % 100

        return f"{hours}:{minutes:02d}:{secs:02d}.{cs:02d}"

    @staticmethod
    def _ass_text(text: str) -> str:
        text = re.sub(r"[\r\n]+", " ", text or "")
        text = text.replace("\\", "").replace("{", "(").replace("}", ")")

        return text.strip()

    def _caption_chunks(self, text: str) -> list[str]:
        """Split the voiceover into short groups of words shown one after another."""

        words = (text or "").split()

        if not words:
            return []

        group_count = math.ceil(len(words) / self.CAPTION_MAX_WORDS)
        per_group = math.ceil(len(words) / group_count)

        return [
            " ".join(words[i : i + per_group]) for i in range(0, len(words), per_group)
        ]

    def _write_captions(self, scenes: list[dict], timeline: list[tuple], path: Path) -> None:
        """
        timeline has one (start, scene_seconds, voice_seconds) per scene.

        The on-screen headline stays for the whole scene. The spoken words are
        split into short chunks, each shown for a share of the voiceover
        proportional to its length. That is an estimate, not exact word timing,
        but speech from a TTS engine is steady enough for it to look in sync.
        """

        lines = [self.ASS_HEADER]

        for scene, (start, scene_seconds, voice_seconds) in zip(scenes, timeline):
            headline = self._ass_text(scene.get("on_screen_text", ""))

            if headline:
                lines.append(
                    f"Dialogue: 0,{self._ass_time(start)},"
                    f"{self._ass_time(start + scene_seconds)},Headline,,0,0,0,,"
                    f"{{\\fad(300,300)}}{headline}\n"
                )

            chunks = self._caption_chunks(scene.get("voiceover", ""))

            if not chunks or voice_seconds <= 0:
                continue

            weights = [len(chunk) + 1 for chunk in chunks]
            total_weight = sum(weights)

            cursor = start + 0.05
            speaking_end = start + voice_seconds

            for chunk, weight in zip(chunks, weights):
                chunk_end = cursor + (speaking_end - start - 0.05) * weight / total_weight

                lines.append(
                    f"Dialogue: 0,{self._ass_time(cursor)},{self._ass_time(chunk_end)},"
                    f"Caption,,0,0,0,,{self._ass_text(chunk)}\n"
                )

                cursor = chunk_end

        path.write_text("".join(lines), encoding="utf-8")

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def render(
        self,
        product_image_path: str,
        reel_payload: dict,
        scene_audio: list,
        output_path: str,
        quality: str = "final",
    ) -> str:
        """
        Render a reel script into an MP4 video.

        Args:
            product_image_path: Path to the product image.
            reel_payload: Reel script dict with 'scenes', 'caption', 'hashtags'.
            scene_audio: One SceneAudio (path + duration) per scene, in order.
            output_path: Where to save the final MP4.
            quality: "final" (1080x1920) or "preview" (720x1280, faster).

        Returns:
            Path to the output MP4 file.
        """

        scenes = reel_payload.get("scenes", [])

        if not scenes or not product_image_path or not scene_audio:
            raise ValueError("Missing required inputs for rendering")

        if len(scene_audio) != len(scenes):
            raise ValueError("There must be one voiceover per scene")

        if quality not in self.QUALITY:
            raise ValueError(f"quality must be one of {list(self.QUALITY)}")

        profile = self.QUALITY[quality]
        self.warnings = []

        background = self.temp_path / "background.jpg"
        self._build_background(product_image_path, str(background))

        clip_names = []
        timeline = []
        cursor = 0.0

        for index, (scene, audio) in enumerate(zip(scenes, scene_audio)):
            scene_seconds = max(audio.duration + self.PAUSE_SECONDS, self.MIN_SCENE_SECONDS)

            clip = self.temp_path / f"scene_{index}.mp4"

            self._render_scene_clip(
                background, audio.path, scene_seconds, index, clip, profile
            )

            clip_names.append(clip.name)
            timeline.append((cursor, scene_seconds, audio.duration))
            cursor += scene_seconds

        self.duration = cursor

        (self.temp_path / "clips.txt").write_text(
            "".join(f"file '{name}'\n" for name in clip_names), encoding="utf-8"
        )

        self._write_captions(scenes, timeline, self.temp_path / "captions.ass")

        output = Path(output_path).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)

        self._join_and_caption(output, profile)

        return str(output)

    def _join_and_caption(self, output: Path, profile: dict) -> None:
        """Join the scene clips and burn in the captions (the second and last FFmpeg pass)."""

        base = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            "clips.txt",
        ]

        encode = [
            "-c:v",
            "libx264",
            "-preset",
            profile["preset"],
            "-crf",
            str(profile["crf"]),
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-movflags",
            "+faststart",
            str(output),
        ]

        try:
            # Run inside the temp folder so the filter can use a plain relative
            # file name (Windows drive-letter paths confuse FFmpeg filter syntax).
            self._run(base + ["-vf", "subtitles=captions.ass"] + encode, timeout=300)
        except RuntimeError as error:
            if "subtitles" not in str(error).lower():
                raise

            # This FFmpeg build cannot burn in captions: still deliver the video.
            self.warnings.append("Captions were skipped: this FFmpeg build has no subtitle support")
            self._run(base + encode, timeout=300)

    def _run(self, command: list[str], timeout: int) -> None:
        try:
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                timeout=timeout,
                cwd=self.temp_dir,
            )
        except subprocess.CalledProcessError as error:
            raise RuntimeError(
                f"FFmpeg failed: {error.stderr.decode(errors='replace')[-800:]}"
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("FFmpeg took too long and was stopped")
        except FileNotFoundError:
            raise RuntimeError(
                "FFmpeg not found. Install it with: winget install Gyan.FFmpeg"
            )
