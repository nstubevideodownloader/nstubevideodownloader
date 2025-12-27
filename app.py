from flask import Flask, render_template, request, jsonify, Response, send_file
import subprocess, os, json
import uuid

app = Flask(__name__)
DOWNLOADS = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOADS, exist_ok=True)

def get_video_info(url):
    try:
        result = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-playlist", url],
            capture_output=True, text=True
        )
        info = json.loads(result.stdout)
        return info
    except:
        return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/info", methods=["POST"])
def info():
    data = request.get_json()
    url = data.get("url")
    info = get_video_info(url)
    if not info:
        return jsonify({"error":"Video tapılmadı"}), 400
    return jsonify({
        "title": info.get("title", "video"),
        "thumbnail": info.get("thumbnail", "")
    })

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")
    dtype = data.get("type")
    quality = data.get("quality", "720")
    kbps = data.get("kbps", "192")

    info = get_video_info(url)
    if not info:
        return "Xəta: Video tapılmadı", 400

    # video adını normalizə et (space -> _)
    title = info.get("title", "video").replace(" ", "_").replace("/", "_")

    if dtype == "mp3":
        out_file = os.path.join(DOWNLOADS, f"{title}.mp3")
        cmd = ["yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", kbps, "-o", out_file, url]
    else:
        out_file = os.path.join(DOWNLOADS, f"{title}.mp4")
        cmd = ["yt-dlp", "-f", f"best[ext=mp4][height<={quality}]", "-o", out_file, url]

    subprocess.run(cmd, check=True)
    return send_file(out_file, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
