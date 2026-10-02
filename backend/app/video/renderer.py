"""
Video renderer: compose product images, text, and voiceover into an MP4.

Uses FFmpeg for composition and handles image scaling, text overlays, and audio mixing.
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont


class VideoRenderer:
    """
    Render a reel script into an Instagram Reel (1080×1920, 9:16).
    """

    # Reel dimensions for Instagram (9:16 aspect ratio).
    WIDTH = 1080
    HEIGHT = 1920
    FPS = 30

    # Fade duration between scenes (seconds).
    FADE_DURATION = 0.5

    # Text styling.
    TEXT_COLOR = (255, 255, 255)  # white
    TEXT_BG_COLOR = (0, 0, 0, 180)  # semi-transparent black
    FONT_SIZE_MAIN = 60
    FONT_SIZE_SMALL = 48

    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="reel_")
        self.temp_path = Path(self.temp_dir)

    def cleanup(self):
        """Remove temporary files."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _scale_image(self, image_path: str, output_path: str) -> None:
        """
        Scale and center the image to fill 1080×1920 while maintaining aspect ratio.
        Add a solid background if needed.
        """

        try:
            img = Image.open(image_path).convert("RGB")
        except Exception:
            # If image fails to open, create a placeholder.
            img = Image.new("RGB", (1080, 1920), color=(128, 128, 128))

        # Calculate scaling to cover the target size.
        target_width, target_height = self.WIDTH, self.HEIGHT
        img_width, img_height = img.size

        scale = max(target_width / img_width, target_height / img_height)

        new_width = int(img_width * scale)
        new_height = int(img_height * scale)

        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Center the scaled image on a solid background.
        bg = Image.new("RGB", (target_width, target_height), color=(30, 30, 30))

        left = (target_width - new_width) // 2
        top = (target_height - new_height) // 2

        bg.paste(img, (left, top))

        bg.save(output_path)

    def _add_text_overlay(
        self,
        image_path: str,
        text: str,
        output_path: str,
        position: str = "bottom",
    ) -> None:
        """
        Add centered text overlay to an image.
        position: 'top', 'center', or 'bottom'
        """

        img = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(img, "RGBA")

        # Try to load a TrueType font; fall back to default.
        font = None
        font_small = None

        font_paths = [
            "/Windows/Fonts/arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]

        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, self.FONT_SIZE_MAIN)
                font_small = ImageFont.truetype(font_path, self.FONT_SIZE_SMALL)
                break
            except (OSError, IOError):
                continue

        if font is None:
            font = ImageFont.load_default()
            font_small = font

        # Wrap text to fit the image width.
        max_width = self.WIDTH - 60  # 30px margin on each side
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            line_text = " ".join(current_line)

            # Estimate line width (rough approximation).
            if len(line_text) * 25 > max_width:  # char width ~ 25px
                current_line.pop()
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        # Draw text with background.
        line_height = 75
        total_height = len(lines) * line_height

        if position == "bottom":
            y_start = self.HEIGHT - total_height - 80
        elif position == "center":
            y_start = (self.HEIGHT - total_height) // 2
        else:  # top
            y_start = 80

        for i, line in enumerate(lines):
            y = y_start + i * line_height

            # Draw semi-transparent background.
            bbox = draw.textbbox((0, 0), line, font=font)
            bbox_width = bbox[2] - bbox[0] + 40
            bbox_height = bbox[3] - bbox[1] + 20

            x_center = (self.WIDTH - bbox_width) // 2

            draw.rectangle(
                [x_center, y - 10, x_center + bbox_width, y + bbox_height],
                fill=self.TEXT_BG_COLOR,
            )

            # Draw text.
            x = (self.WIDTH - (bbox[2] - bbox[0])) // 2
            draw.text((x, y), line, fill=self.TEXT_COLOR, font=font)

        img.save(output_path)

    def _create_scene_frames(
        self,
        image_path: str,
        on_screen_text: str,
        duration_frames: int,
    ) -> list:
        """
        Create a series of frames for one scene (with text overlay).
        Returns list of frame file paths.
        """

        frames = []

        scaled_image = self.temp_path / f"scaled_{len(frames)}.png"
        self._scale_image(image_path, str(scaled_image))

        text_image = self.temp_path / f"text_{len(frames)}.png"
        self._add_text_overlay(str(scaled_image), on_screen_text, str(text_image))

        # Create frames for the duration.
        for frame_idx in range(duration_frames):
            frame_path = self.temp_path / f"frame_{len(frames):05d}.png"
            Image.open(str(text_image)).save(str(frame_path))
            frames.append(str(frame_path))

        return frames

    def render(
        self,
        product_image_path: str,
        reel_payload: dict,
        voiceover_audio_path: str,
        output_path: str,
    ) -> str:
        """
        Render a reel script into an MP4 video.

        Args:
            product_image_path: Path to the product image.
            reel_payload: Reel script dict with 'scenes', 'caption', 'hashtags'.
            voiceover_audio_path: Path to the combined voiceover WAV file.
            output_path: Where to save the final MP4.

        Returns:
            Path to the output MP4 file.
        """

        frames = []
        scenes = reel_payload.get("scenes", [])

        if not scenes or not product_image_path or not voiceover_audio_path:
            raise ValueError("Missing required inputs for rendering")

        # Create frames for each scene.
        # Assume equal time per scene (rough estimate from voiceover length).
        frame_duration_per_scene = (self.FPS * 8)  # ~8 seconds per scene

        for scene_idx, scene in enumerate(scenes):
            scene_frames = self._create_scene_frames(
                product_image_path,
                scene.get("on_screen_text", ""),
                frame_duration_per_scene,
            )

            frames.extend(scene_frames)

        if not frames:
            raise ValueError("No frames generated")

        # Use FFmpeg to create video from frames and add audio.
        frame_pattern = str(self.temp_path / "frame_%05d.png")

        cmd = [
            "ffmpeg",
            "-framerate",
            str(self.FPS),
            "-i",
            frame_pattern,
            "-i",
            voiceover_audio_path,
            "-c:v",
            "libx264",
            "-crf",
            "23",  # quality (lower = better, but slower)
            "-c:a",
            "aac",
            "-shortest",
            "-y",
            output_path,
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=300)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg failed: {e.stderr.decode()}")
        except FileNotFoundError:
            raise RuntimeError(
                "FFmpeg not found. Install it with: winget install Gyan.FFmpeg"
            )

        return output_path
