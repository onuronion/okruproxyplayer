
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
import requests
import re
import html
import json
import uvicorn

app = FastAPI()

VIDEO_URLS = {}
VIDEO_INFO = {}

QUALITY_NAMES = {
    "mobile": "Mobil",
    "lowest": "240p",
    "low": "360p",
    "sd": "480p",
    "hd": "720p",
    "full": "1080p"
}


def get_metadata(embed_url):
    match = re.search(r'/videoembed/(\d+)', embed_url)

    if not match:
        raise Exception("Geçersiz OK.ru videoembed linki")

    video_id = match.group(1)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(
        f"https://ok.ru/videoembed/{video_id}",
        headers=headers,
        timeout=20
    )

    response.raise_for_status()
    page = html.unescape(response.text)

    marker = '"metadata":"'
    start = page.find(marker)

    if start == -1:
        raise Exception("Metadata bulunamadı")

    start += len(marker)
    escaped = False
    end = start

    while end < len(page):
        c = page[end]

        if c == '"' and not escaped:
            break

        if c == "\\" and not escaped:
            escaped = True
        else:
            escaped = False

        end += 1

    metadata_string = page[start:end]
    metadata_string = json.loads('"' + metadata_string + '"')

    return json.loads(metadata_string)


@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OK.ru Player</title>
<link rel="stylesheet" href="https://vjs.zencdn.net/8.23.4/video-js.css">
<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #0b0f14;
    color: white;
    font-family: Arial, Helvetica, sans-serif;
}

.container {
    width: 95%;
    max-width: 1100px;
    margin: 30px auto;
}

.title {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 20px;
}

.video-js {
    width: 100%;
    aspect-ratio: 16 / 9;
}

.controls {
    margin-top: 15px;
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

select {
    background: #151c25;
    color: white;
    border: 1px solid #344150;
    padding: 11px 15px;
    border-radius: 7px;
    font-size: 15px;
    outline: none;
}

button {
    background: #1683ff;
    color: white;
    border: 0;
    padding: 11px 18px;
    border-radius: 7px;
    cursor: pointer;
    font-size: 15px;
}

button:hover {
    background: #086bd6;
}

.info {
    margin-top: 15px;
    color: #8995a3;
    font-size: 14px;
}

#loading {
    margin-top: 15px;
    color: #53a8ff;
    display: none;
}
</style>
</head>
<body>
<div class="container">
    <div class="title">OK.ru Video Player</div>

    <video
        id="player"
        class="video-js vjs-big-play-centered"
        controls
        preload="auto">
    </video>

    <div class="controls">
        <select id="quality">
            <option value="">Kaliteler yükleniyor...</option>
        </select>

        <button onclick="changeQuality()">Kaliteyi Değiştir</button>
    </div>

    <div id="loading">Video yükleniyor...</div>
    <div class="info" id="info">Bilgiler alınıyor...</div>
</div>

<script src="https://vjs.zencdn.net/8.23.4/video.min.js"></script>
<script>
let player;

document.addEventListener("DOMContentLoaded", async function() {
    player = videojs("player", {
        controls: true,
        autoplay: false,
        preload: "metadata",
        responsive: true,
        fluid: true
    });

    await loadInfo();
});

async function loadInfo() {
    try {
        const response = await fetch("/api/info");
        const data = await response.json();

        if (!data.success) {
            document.getElementById("info").innerText = data.error;
            return;
        }

        const select = document.getElementById("quality");
        select.innerHTML = "";

        for (const quality of data.qualities) {
            const option = document.createElement("option");
            option.value = quality.name;
            option.textContent = quality.label;
            select.appendChild(option);
        }

        document.getElementById("info").innerText =
            data.title + " • " + data.width + "x" +
            data.height + " • " + data.duration + " saniye";

        if (data.default_quality) {
            select.value = data.default_quality;
            loadVideo(data.default_quality);
        }
    } catch (error) {
        console.error(error);
        document.getElementById("info").innerText =
            "Video bilgileri alınamadı.";
    }
}

function loadVideo(quality) {
    const url = "/video.mp4?quality=" + encodeURIComponent(quality);

    player.src({
        src: url,
        type: "video/mp4"
    });
}

function changeQuality() {
    const quality = document.getElementById("quality").value;
    const currentTime = player.currentTime();
    const wasPlaying = !player.paused();

    document.getElementById("loading").style.display = "block";

    player.one("loadedmetadata", function() {
        try {
            player.currentTime(currentTime);
        } catch (error) {}

        if (wasPlaying) {
            player.play().catch(() => {});
        }

        document.getElementById("loading").style.display = "none";
    });

    loadVideo(quality);
}
</script>
</body>
</html>
"""


@app.get("/api/info")
def api_info():
    if not VIDEO_URLS:
        return JSONResponse({
            "success": False,
            "error": "Video bulunamadı"
        })

    qualities = [
        {
            "name": name,
            "label": QUALITY_NAMES.get(name, name)
        }
        for name in VIDEO_URLS
    ]

    priority = ["full", "hd", "sd", "low", "lowest", "mobile"]
    default_quality = next(
        (quality for quality in priority if quality in VIDEO_URLS),
        None
    )

    return {
        "success": True,
        "title": VIDEO_INFO.get("title", "OK.ru Video"),
        "width": VIDEO_INFO.get("width", 0),
        "height": VIDEO_INFO.get("height", 0),
        "duration": VIDEO_INFO.get("duration", 0),
        "qualities": qualities,
        "default_quality": default_quality
    }


@app.get("/video.mp4")
def video(request: Request, quality: str = "sd"):
    if quality not in VIDEO_URLS:
        priority = ["full", "hd", "sd", "low", "lowest", "mobile"]
        quality = next(
            (item for item in priority if item in VIDEO_URLS),
            None
        )

    if not quality:
        raise HTTPException(
            status_code=404,
            detail="Video bulunamadı"
        )

    url = VIDEO_URLS[quality]

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36"
        ),
        "Referer": "https://ok.ru/",
        "Accept": "*/*"
    }

    range_header = request.headers.get("range")

    if range_header:
        headers["Range"] = range_header

    try:
        response = requests.get(
            url,
            headers=headers,
            stream=True,
            timeout=30
        )
    except requests.RequestException:
        raise HTTPException(
            status_code=502,
            detail="Video sunucusuna bağlanılamadı"
        )

    if response.status_code not in (200, 206):
        status_code = response.status_code
        response.close()
        raise HTTPException(
            status_code=status_code,
            detail="OKCDN video alınamadı"
        )

    response_headers = {
        "Accept-Ranges": "bytes",
        "Content-Disposition": "inline",
        "Cache-Control": "no-cache"
    }

    for header in [
        "Content-Length",
        "Content-Range",
        "Content-Type",
        "Accept-Ranges"
    ]:
        value = response.headers.get(header)

        if value:
            response_headers[header] = value

    def stream_video():
        try:
            for chunk in response.iter_content(chunk_size=512 * 1024):
                if chunk:
                    yield chunk
        finally:
            response.close()

    return StreamingResponse(
        stream_video(),
        status_code=response.status_code,
        media_type=response.headers.get("Content-Type", "video/mp4"),
        headers=response_headers
    )


if __name__ == "__main__":
    embed_url = input("OK.ru Embed linkini gir: ").strip()

    print()
    print("Metadata alınıyor...")
    print()

    try:
        metadata = get_metadata(embed_url)

        VIDEO_URLS.clear()
        VIDEO_INFO.clear()

        movie = metadata.get("movie", {})

        VIDEO_INFO["title"] = movie.get("title", "OK.ru Video")
        VIDEO_INFO["width"] = movie.get("width", 0)
        VIDEO_INFO["height"] = movie.get("height", 0)
        VIDEO_INFO["duration"] = movie.get("duration", 0)

        for video_data in metadata.get("videos", []):
            name = video_data.get("name")
            url = video_data.get("url")

            if name and url:
                VIDEO_URLS[name] = url

        print("=" * 60)
        print("Video:", VIDEO_INFO["title"])
        print("Mevcut kaliteler:")

        for quality in VIDEO_URLS:
            print("-", QUALITY_NAMES.get(quality, quality))

        print("=" * 60)
        print()
        print("Player: http://localhost:8000")
        print()

        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000
        )

    except Exception as error:
        print()
        print("HATA:")
        print(error)
