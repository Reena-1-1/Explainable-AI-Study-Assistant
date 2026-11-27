
"""YouTube transcript extraction for StudyLens AI."""

import re
from urllib.parse import urlparse, parse_qs

from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url):
    """Extract the YouTube video ID from a supported URL."""

    parsed = urlparse(url.strip())
    host = parsed.netloc.lower().split(":")[0]

    if host in ("youtube.com", "www.youtube.com", "m.youtube.com"):
        video_id = parse_qs(parsed.query).get("v", [None])[0]

    elif host == "youtu.be" or host == "www.youtu.be":
        video_id = parsed.path.strip("/").split("/")[0]

    else:
        raise ValueError("Please enter a valid YouTube video URL.")

    if not video_id or not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise ValueError("Could not find a valid YouTube video ID.")

    return video_id


def extract_youtube_transcript(url):
    """Fetch an available transcript and return its text."""

    video_id = extract_video_id(url)

    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id)

        transcript_text = " ".join(
            snippet.text for snippet in transcript
        ).strip()

        if not transcript_text:
            raise ValueError("The video transcript is empty.")

        return {
            "video_id": video_id,
            "url": url.strip(),
            "text": transcript_text
        }

    except Exception as error:
        raise ValueError(
            f"Could not extract the transcript. The video may not have "
            f"available captions. Details: {error}"
        ) from error
