from yt_dlp import YoutubeDL

def download_audio(url: str):

    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "outtmpl": "./data/%(title).200s",
        "restrictfilenames": True,

        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "0",
        }],

        "extractor_args": {"youtube": {"player_client": ["android"]}},
        "forceip": "ipv4",

        "retries": 10,
        "fragment_retries": 10,
        "concurrent_fragment_downloads": 1,
        "sleep_requests": 1,
        "retry_sleep": [2, 4, 8, 16],
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        for rd in info.get("requested_downloads") or []:
            if rd.get("filepath"):
                return rd["filepath"]
