import os
import uuid
import soundfile as sf
from flask import Flask, render_template, request, jsonify, send_file
from kittentts import KittenTTS
from gtts import gTTS
from deep_translator import GoogleTranslator

app = Flask(__name__)

# Directory to store generated audio files
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "static", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

# Available voice models for KittenTTS (English)
VOICES = ["Bella", "Jasper", "Luna", "Bruno", "Rosie", "Hugo", "Kiki", "Leo"]

# Available TTS models (different sizes)
MODELS = {
    "Mini (80M - Best Quality)": "KittenML/kitten-tts-mini-0.8",
    "Micro (40M - Balanced)": "KittenML/kitten-tts-micro-0.8",
    "Nano (15M - Fastest)": "KittenML/kitten-tts-nano-0.8",
}

# Languages with their gTTS language codes
LANGUAGES = {
    "English": "en",
    "Malayalam": "ml",
    "Hindi": "hi",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Bengali": "bn",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Punjabi": "pa",
    "Urdu": "ur",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Japanese": "ja",
    "Chinese": "zh-CN",
    "Korean": "ko",
    "Arabic": "ar",
    "Russian": "ru",
}

# Cache loaded KittenTTS models
loaded_models = {}


def get_model(model_key):
    """Load and cache a KittenTTS model."""
    if model_key not in loaded_models:
        model_name = MODELS.get(model_key, MODELS["Mini (80M - Best Quality)"])
        print(f"Loading model: {model_name}...")
        loaded_models[model_key] = KittenTTS(model_name)
        print(f"Model loaded: {model_name}")
    return loaded_models[model_key]


def translate_text(text, target_lang_code):
    """Translate text from English to target language."""
    if target_lang_code == "en":
        return text
    try:
        translated = GoogleTranslator(source="auto", target=target_lang_code).translate(text)
        return translated if translated else text
    except Exception as e:
        print(f"Translation error: {e}")
        return text


@app.route("/")
def index():
    return render_template(
        "index.html",
        voices=VOICES,
        models=list(MODELS.keys()),
        languages=list(LANGUAGES.keys()),
    )


@app.route("/translate", methods=["POST"])
def translate():
    """Translate text to the selected language."""
    data = request.get_json()
    text = data.get("text", "").strip()
    language = data.get("language", "English")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    lang_code = LANGUAGES.get(language, "en")
    translated = translate_text(text, lang_code)

    return jsonify({
        "success": True,
        "translated_text": translated,
        "language": language,
    })


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    text = data.get("text", "").strip()
    voice = data.get("voice", "Bella")
    model_key = data.get("model", "Mini (80M - Best Quality)")
    speed = float(data.get("speed", 1.0))
    language = data.get("language", "English")

    if not text:
        return jsonify({"error": "Please enter some text"}), 400

    lang_code = LANGUAGES.get(language, "en")

    try:
        # Translate text if language is not English
        translated_text = translate_text(text, lang_code)

        filename = f"{uuid.uuid4().hex}.wav"
        filepath = os.path.join(AUDIO_DIR, filename)

        if language == "English":
            # Use KittenTTS for English (better quality with voice selection)
            if voice not in VOICES:
                voice = "Bella"
            model = get_model(model_key)
            audio = model.generate(translated_text, voice=voice, speed=speed)
            sf.write(filepath, audio, 24000)
        else:
            # Use gTTS for non-English languages (actually supports the language)
            mp3_path = filepath.replace(".wav", ".mp3")
            tts = gTTS(text=translated_text, lang=lang_code, slow=(speed < 0.8))
            tts.save(mp3_path)
            # Convert mp3 to wav is not needed, just serve mp3
            filename = filename.replace(".wav", ".mp3")
            filepath = mp3_path

        return jsonify({
            "success": True,
            "audio_url": f"/static/audio/{filename}",
            "download_url": f"/download/{filename}",
            "filename": filename,
            "translated_text": translated_text,
            "language": language,
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/download/<filename>")
def download(filename):
    filepath = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    return send_file(filepath, as_attachment=True, download_name=f"tts_{filename}")


if __name__ == "__main__":
    # Pre-load default model on startup
    print("Pre-loading default model...")
    get_model("Mini (80M - Best Quality)")
    print("Ready!")
    app.run(debug=True, host="0.0.0.0", port=5000)
