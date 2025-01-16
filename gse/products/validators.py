import subprocess
import tempfile

import magic
from django.core.exceptions import ValidationError


def validate_file_type(file, expected_types: dict) -> str | None:
    buffered = file.read(2048)
    mime_type = magic.from_buffer(buffered, mime=True)
    file.seek(0)
    if mime_type in expected_types.get('images'):
        return 'image'
    elif mime_type in expected_types.get('videos'):
        return 'video'
    else:
        return None


def get_video_duration(file_path):
    ffprobe_path = "ffprobe"
    try:
        result = subprocess.run(
            [ffprobe_path, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        return float(result.stdout)
    except Exception as e:
        raise ValidationError(f"Error reading video file: {str(e)}")


class VideoDurationValidator:
    def __init__(self, max_duration):
        self.max_duration = max_duration

    def __call__(self, video_file):
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            for chunk in video_file.chunks():
                temp_file.write(chunk)
            temp_file.flush()
            try:
                duration = get_video_duration(temp_file.name)
            except ValidationError as e:
                raise e
            except Exception:
                raise ValidationError("Could not process the video file.")

            if duration > self.max_duration:
                raise ValidationError(
                    {
                        'media': f"Video duration exceeds the limit. Maximum allowed is {self.max_duration} seconds, but got {duration:.2f} seconds."}
                )
