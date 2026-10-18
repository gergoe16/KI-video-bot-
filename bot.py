import json
import math
import random
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import wave
from datetime import datetime
from pathlib import Path

try:
    import pyttsx3
    from PIL import Image, ImageDraw, ImageFont
    import imageio_ffmpeg
except ImportError as exc:
    print("Es fehlen Python-Pakete. Bitte zuerst INSTALL.bat ausführen.")
    print("Details:", exc)
    input("Enter zum Beenden...")
    sys.exit(1)

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
MODEL = "llama3.2"
OLLAMA_URL = "http://localhost:11434/api/generate"
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
SCENE_COUNT = 6

TOPICS = [
    "5 erstaunliche Fakten über das Weltall",
    "Psychologische Fakten über Gewohnheiten",
    "Die überraschende Geschichte eines Alltagsgegenstands",
    "Wissenschaftliche Rätsel, die leicht erklärt werden",
    "Unglaubliche Fakten über Tiere",
    "Technologie, die unsere Zukunft verändert",
    "Historische Irrtümer, die viele Menschen glauben",
    "Einfache Produktivitätstipps für den Alltag",
]

COLORS = [
    ("#101828", "#344054", "#FEC84B"),
    ("#14213D", "#23395B", "#FCA311"),
    ("#132A24", "#245B4A", "#9FE870"),
    ("#251641", "#523080", "#D7B8FF"),
    ("#3A1728", "#6B2D45", "#FFB4C2"),
    ("#102A43", "#1F5A75", "#7DE3F5"),
]

def ask_ollama():
    topic_hint = random.choice(TOPICS)
    prompt = f"""
Du bist Autor für informative deutschsprachige Kurzvideos für TikTok und YouTube Shorts.
Wähle selbst ein interessantes, seriöses Thema. Eine mögliche Inspiration ist: {topic_hint}
Schreibe ein Video für etwa 35 bis 50 Sekunden. Keine unbelegten sensationellen Behauptungen,
keine medizinischen oder finanziellen Versprechen. Schreibe natürliches Deutsch.
Antworte ausschließlich mit gültigem JSON in dieser Form:
{{
  "title": "kurzer Titel",
  "topic": "Thema",
  "script": "vollständiger gesprochener Text ohne Regieanweisungen",
  "scenes": ["kurzer Text für Szene 1", "Text für Szene 2", "Text für Szene 3", "Text für Szene 4", "Text für Szene 5", "Text für Szene 6"],
  "description": "kurze Videobeschreibung mit passenden Hashtags"
}}
Die sechs Szenentexte sollen zum gesprochenen Skript passen, jeweils kurz und gut lesbar sein.
"""
    payload = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.85}
    }).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL, data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=240) as response:
        result = json.loads(response.read().decode("utf-8"))
    data = json.loads(result.get("response", "{}"))
    title = str(data.get("title", "Wusstest du das?")).strip()
    script = str(data.get("script", "")).strip()
    scenes = data.get("scenes", [])
    description = str(data.get("description", "#Wissen #Shorts")).strip()
    if not script or not isinstance(scenes, list) or len(scenes) < 3:
        raise ValueError("Das Modell hat kein vollständiges Skript geliefert.")
    scenes = [str(s).strip() for s in scenes if str(s).strip()][:SCENE_COUNT]
    while len(scenes) < SCENE_COUNT:
        scenes.append(scenes[-1])
    return {
        "title": title[:100],
        "topic": str(data.get("topic", title)).strip(),
        "script": script,
        "scenes": scenes,
        "description": description
    }

def fallback_content():
    topic = random.choice(TOPICS)
    title = topic
    script = (
        f"Heute geht es um {topic.lower()}. Unser Alltag steckt voller Dinge, "
        "die auf den ersten Blick ganz gewöhnlich wirken. Wenn man genauer hinsieht, "
        "entdeckt man spannende Zusammenhänge. Frage bei überraschenden Behauptungen "
        "immer nach verlässlichen Quellen und prüfe, was wirklich belegt ist. "
        "Wissen wird besonders interessant, wenn man neugierig bleibt und weiterfragt."
    )
    return {
        "title": title,
        "topic": topic,
        "script": script,
        "scenes": [
            topic, "Sieh genauer hin", "Hintergründe entdecken",
            "Behauptungen überprüfen", "Quellen sind wichtig",
            "Bleib neugierig!"
        ],
        "description": f"{topic} #Wissen #Shorts #TikTok"
    }

def load_font(size, bold=False):
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for path in candidates:
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size)
            except OSError:
                pass
    return ImageFont.load_default()

def wrap_text(draw, text, font, max_width):
    words = re.sub(r"\s+", " ", text).split()
    lines, current = [], ""
    for word in words:
        trial = word if not current else current + " " + word
        if draw.textbbox((0, 0), trial, font=font)[2] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]

def make_scene_image(text, index, out_path, title):
    color_a, color_b, accent = COLORS[index % len(COLORS)]
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), color_a)
    draw = ImageDraw.Draw(img)
    # Simple diagonal gradient, with no extra dependencies.
    rgb_a = tuple(int(color_a[i:i+2], 16) for i in (1, 3, 5))
    rgb_b = tuple(int(color_b[i:i+2], 16) for i in (1, 3, 5))
    for y in range(VIDEO_HEIGHT):
        t = y / max(1, VIDEO_HEIGHT - 1)
        c = tuple(int(rgb_a[k] * (1-t) + rgb_b[k] * t) for k in range(3))
        draw.line((0, y, VIDEO_WIDTH, y), fill=c)
    # Decorative shapes.
    draw.ellipse((760, 120, 1180, 540), outline=accent, width=8)
    draw.ellipse((-170, 1370, 260, 1800), outline=accent, width=8)
    draw.rounded_rectangle((72, 105, 390, 174), radius=28, fill=accent)
    draw.text((100, 122), "WISSEN IN KURZ", font=load_font(27, True), fill="#101828")
    draw.text((75, 240), f"{index + 1:02d}  /  {SCENE_COUNT:02d}", font=load_font(31, True), fill="#FFFFFF")

    safe_text = text.strip()
    font_size = 76
    max_width = VIDEO_WIDTH - 150
    while font_size >= 42:
        font = load_font(font_size, True)
        lines = wrap_text(draw, safe_text, font, max_width)
        line_h = font_size + 22
        if len(lines) * line_h <= 760:
            break
        font_size -= 4
    line_h = font_size + 22
    block_h = len(lines) * line_h
    y = (VIDEO_HEIGHT - block_h) // 2
    # Dark rounded panel behind the words.
    panel_top = max(410, y - 65)
    panel_bottom = min(1430, y + block_h + 70)
    draw.rounded_rectangle((54, panel_top, VIDEO_WIDTH - 54, panel_bottom),
                           radius=42, fill="#101828")
    y = (VIDEO_HEIGHT - block_h) // 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        draw.text(((VIDEO_WIDTH - line_w) / 2, y), line, font=font, fill="#FFFFFF")
        y += line_h
    # Progress marker and title footer.
    bar_y = 1660
    draw.rounded_rectangle((80, bar_y, VIDEO_WIDTH - 80, bar_y + 12), radius=6, fill="#FFFFFF")
    progress_right = 80 + int((VIDEO_WIDTH - 160) * (index + 1) / SCENE_COUNT)
    draw.rounded_rectangle((80, bar_y, progress_right, bar_y + 12), radius=6, fill=accent)
    footer = title[:46]
    footer_font = load_font(28)
    draw.text((80, 1720), footer, font=footer_font, fill="#FFFFFF")
    draw.text((80, 1800), "Folge für mehr kurze Fakten", font=load_font(27), fill=accent)
    img.save(out_path, "PNG")

def make_voice(text, path):
    engine = pyttsx3.init()
    # Prefer a German Windows voice when one is available.
    try:
        voices = engine.getProperty("voices")
        for voice in voices:
            info = (str(getattr(voice, "name", "")) + " " + str(getattr(voice, "id", ""))).lower()
            if any(term in info for term in ("german", "deutsch", "de-de", "heda", "katja", "stefan")):
                engine.setProperty("voice", voice.id)
                break
    except Exception:
        pass
    engine.setProperty("rate", 168)
    engine.setProperty("volume", 1.0)
    engine.save_to_file(text, str(path))
    engine.runAndWait()
    engine.stop()
    if not path.exists() or path.stat().st_size < 1000:
        raise RuntimeError("Die Windows-Sprachausgabe hat keine Audiodatei erstellt.")

def audio_duration(path):
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes() / float(wav.getframerate())

def ffconcat_quote(path):
    return str(path.resolve()).replace("\\", "/").replace("'", "'\\''")

def render_video(content, work_dir, output_path, audio_path):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    duration = audio_duration(audio_path)
    scenes = content["scenes"]
    images = []
    for i, text in enumerate(scenes):
        image_path = work_dir / f"scene_{i+1:02d}.png"
        make_scene_image(text, i, image_path, content["title"])
        images.append(image_path)
    concat_path = work_dir / "scenes.txt"
    per_scene = max(1.0, duration / len(images))
    with concat_path.open("w", encoding="utf-8") as f:
        f.write("ffconcat version 1.0\n")
        for image_path in images:
            f.write("file '" + ffconcat_quote(image_path) + "'\n")
            f.write(f"duration {per_scene:.4f}\n")
        f.write("file '" + ffconcat_quote(images[-1]) + "'\n")
    cmd = [
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
        "-safe", "0", "-f", "concat", "-i", str(concat_path),
        "-i", str(audio_path),
        "-vf", "fps=30,scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "24",
        "-c:a", "aac", "-b:a", "160k", "-t", f"{duration:.3f}",
        "-shortest", "-movflags", "+faststart", str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise RuntimeError("FFmpeg konnte das Video nicht erstellen:\n" + result.stderr[-2500:])

def main():
    print("=" * 58)
    print("          KOSTENLOSER KI VIDEO BOT")
    print("=" * 58)
    print("Thema und Skript werden lokal mit Ollama erstellt.\n")
    OUTPUT_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    work_dir = OUTPUT_DIR / f"projekt_{stamp}"
    work_dir.mkdir(parents=True, exist_ok=True)

    try:
        print(f"Frage lokales KI-Modell ({MODEL}) nach einem Thema ...")
        content = ask_ollama()
        print("Das KI-Skript wurde erstellt.")
    except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print("\nOllama ist nicht erreichbar oder die Antwort war ungültig.")
        print("Prüfe, ob Ollama läuft und das Modell mit 'ollama pull llama3.2' installiert ist.")
        print("Details:", exc)
        print("\nIch verwende für diesen Lauf ein eingebautes Beispielskript.")
        content = fallback_content()

    print("\nTitel:", content["title"])
    print("\nSkript:\n", content["script"])
    (work_dir / "skript.txt").write_text(
        content["title"] + "\n\n" + content["script"] + "\n\n" + content["description"],
        encoding="utf-8"
    )
    audio_path = work_dir / "sprache.wav"
    print("\nErzeuge Sprachaufnahme ...")
    try:
        make_voice(content["script"], audio_path)
    except Exception as exc:
        print("\nFEHLER bei der Sprachaufnahme:", exc)
        print("Prüfe in Windows, ob eine Sprachausgabe verfügbar ist.")
        input("Enter zum Beenden...")
        return

    output_path = OUTPUT_DIR / f"short_{stamp}.mp4"
    print("Erzeuge vertikales Video ...")
    try:
        render_video(content, work_dir, output_path, audio_path)
    except Exception as exc:
        print("\nFEHLER beim Rendern:", exc)
        input("Enter zum Beenden...")
        return

    metadata_path = OUTPUT_DIR / f"short_{stamp}_beschreibung.txt"
    metadata_path.write_text(
        "TITEL\n" + content["title"] + "\n\nBESCHREIBUNG / HASHTAGS\n" +
        content["description"] + "\n\nSKRIPT\n" + content["script"] + "\n",
        encoding="utf-8"
    )
    print("\nFERTIG!")
    print("Video:       ", output_path.resolve())
    print("Beschreibung:", metadata_path.resolve())
    print("Skript:      ", (work_dir / "skript.txt").resolve())
    print("\nDas Video wurde noch nicht hochgeladen. Du kannst die MP4-Datei selbst posten.")
    input("\nDrücke Enter zum Schließen...")

if __name__ == "__main__":
    main()
