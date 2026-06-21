#!/usr/bin/env python3
"""轻量 edge-tts 语音服务 - 为日语单词复习站提供语音"""

import subprocess, tempfile, os, hashlib
from flask import Flask, request, send_file, jsonify, make_response

app = Flask(__name__)

CACHE_DIR = os.path.expanduser("~/.hermes/tts_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

VOICE = "ja-JP-NanamiNeural"  # 微软日语神经语音，最自然的女声
RATE = "+0%"  # 正常语速

def cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    return resp

@app.route("/tts")
def tts():
    text = request.args.get("text", "")
    if not text:
        return cors(jsonify({"error": "missing text"})), 400

    key = hashlib.md5(text.encode()).hexdigest()
    cache_path = os.path.join(CACHE_DIR, f"{key}.mp3")

    if not os.path.exists(cache_path):
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        tmp.close()
        try:
            subprocess.run(
                ["edge-tts", "--voice", VOICE, "--rate", RATE,
                 "--text", text, "--write-media", tmp.name],
                check=True, capture_output=True, timeout=30
            )
            os.rename(tmp.name, cache_path)
        except Exception as e:
            os.unlink(tmp.name)
            return cors(jsonify({"error": str(e)})), 500

    return cors(send_file(cache_path, mimetype="audio/mpeg"))

@app.route("/ping")
def ping():
    return cors(jsonify({"status": "ok", "voice": VOICE}))

if __name__ == "__main__":
    print(f"🧪 Edge TTS 服务启动 → http://localhost:8765")
    print(f"   语音: {VOICE}")
    print(f"   测试: http://localhost:8765/tts?text=こんにちは")
    app.run(host="127.0.0.1", port=8765, debug=False)
