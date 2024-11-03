import speech_recognition as sr
from gtts import gTTS
import streamlit as st
import os
import google.generativeai as genai
from datetime import datetime
import pytz

# Set page configuration
st.set_page_config(
    layout="wide",
    page_title="Multilingual Chat Translator Pro",
    page_icon="🌐"
)

# Enhanced CSS with improved visibility
st.markdown("""
<style>
.main {
    padding: 2rem;
}
.chat-container {
    border-radius: 15px;
    padding: 20px;
    margin: 10px 0;
    background: #f8f9fa;
}
.user1-message {
    background: linear-gradient(135deg, #ff9800, #f44336);
    color: white;
    margin-right: 15%;
    border-radius: 18px 18px 18px 5px;
    padding: 18px;
    margin-bottom: 20px;
    box-shadow: 0 3px 15px rgba(0,0,0,0.2);
}
.user2-message {
    background: linear-gradient(135deg, #4caf50, #2e7d32);
    color: white;
    margin-left: 15%;
    border-radius: 18px 18px 5px 18px;
    padding: 18px;
    margin-bottom: 20px;
    box-shadow: 0 3px 15px rgba(0,0,0,0.2);
}
.original-text {
    font-size: 18px;
    font-weight: 500;
    margin-bottom: 10px;
    line-height: 1.5;
}
.translated-text {
    font-size: 16px;
    color: rgba(255,255,255,0.95);
    margin-top: 10px;
    border-top: 1px solid rgba(255,255,255,0.3);
    padding-top: 10px;
    line-height: 1.4;
}
.timestamp {
    font-size: 12px;
    color: rgba(255,255,255,0.8);
    text-align: right;
    margin-top: 8px;
}
.stButton > button {
    width: 100%;
    border-radius: 25px;
    height: 45px;
    font-weight: 600;
    transition: all 0.3s ease;
    background-color: #ff7043;
    color: white;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}
.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
}
.speech-button {
    background-color: #0288d1 !important;
    color: white !important;
}
.send-button {
    background-color: #43a047 !important;
    color: white !important;
}
div[data-baseweb="select"] {
    background-color: #e0f7fa;
    border-radius: 10px;
    padding: 5px;
    margin-bottom: 10px;
}
div[data-baseweb="select"] > div {
    background-color: #e0f7fa;
    color: #006064;
    font-weight: 500;
}
.stTextArea > div > div {
    border-radius: 15px;
    border: 2px solid #26c6da;
    background-color: #e1f5fe;
}
.stTextArea > div > div:focus-within {
    border-color: #00bcd4;
}
.sidebar .element-container {
    background-color: #fafafa;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 15px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# Language options with flags
LANGUAGE_OPTIONS = {
    "Hindi": "hi",
    "Kannada": "kn",
    "Telugu": "te",
    "Tamil": "ta",
    "Malayalam": "ml",
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Chinese": "zh-CN",
    "Japanese": "ja",
    "Russian": "ru"
}

# Initialize Gemini API
genai.configure(api_key='AIzaSyBRR11qYnVOwPdDLwlNliGU9rt_P0YxNCc')

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def format_timestamp(iso_timestamp):
    """Format timestamp for better readability"""
    dt = datetime.fromisoformat(iso_timestamp)
    return dt.strftime("%B %d, %Y at %I:%M %p")

def recognize_speech(language_code):
    """Enhanced speech recognition with better error handling"""
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.info("🎤 Listening... Please speak clearly")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=10)
            st.success("Processing your speech...")
            text = recognizer.recognize_google(audio, language=language_code)
            return text
    except sr.UnknownValueError:
        st.error("Sorry, I couldn't understand that. Please try again.")
    except sr.RequestError:
        st.error("There was an error with the speech recognition service. Please try again.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
    return None

def translate_text(input_text, source_language, target_language):
    """Translate text using Gemini with enhanced error handling"""
    try:
        # Ensure language codes are correctly recognized
        language_mapping = {
            'hi': 'Hindi',
            'kn': 'Kannada',
            'te': 'Telugu',
            'ta': 'Tamil',
            'ml': 'Malayalam',
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'zh-CN': 'Chinese',
            'ja': 'Japanese',
            'ru': 'Russian'
        }

        source_language_name = language_mapping.get(source_language, source_language)
        target_language_name = language_mapping.get(target_language, target_language)

        model = genai.GenerativeModel('gemini-pro')
        prompt = f"Translate this text from {source_language_name} to {target_language_name}: {input_text}"
        response = model.generate_content(prompt)
        return response.text.strip() if response and response.text else None
    except Exception as e:
        st.error(f"Translation error: {str(e)}")
        return None

def text_to_speech(text, language_code='en'):
    """Enhanced text-to-speech with better file management"""
    try:
        tts = gTTS(text=text, lang=language_code)
        audio_file = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.mp3"
        tts.save(audio_file)
        return audio_file
    except Exception as e:
        st.error(f"Text-to-speech error: {str(e)}")
        return None

def display_message(msg, column):
    """Display chat message with enhanced styling"""
    message_class = "user1-message" if msg["user"] == "user1" else "user2-message"
    with column:
        st.markdown(f"""
            <div class="{message_class}">
                <div class="original-text">{msg.get('original_text', '')}</div>
                <div class="translated-text">🔄 {msg.get('translated_text', '')}</div>
                <div class="timestamp">{format_timestamp(msg['timestamp'])}</div>
            </div>
        """, unsafe_allow_html=True)

        if msg.get('audio_file') and os.path.exists(msg['audio_file']):
            with open(msg['audio_file'], 'rb') as audio:
                st.audio(audio.read(), format='audio/mp3')

def add_message_to_history(user, text, translated, audio_file):
    """Add message to chat history"""
    st.session_state.chat_history.append({
        "user": user,
        "timestamp": datetime.now().isoformat(),
        "original_text": text,
        "translated_text": translated,
        "audio_file": audio_file
    })
    return True

def handle_user_input(user_number, user_lang, target_lang, column):
    """Handle user input with improved error handling"""
    with column:
        text_input = st.text_area(
            "",
            key=f"text_input_user{user_number}",
            height=100,
            placeholder="Type your message here..."
        )

        # Buttons in a single row
        button_cols = st.columns([1, 1])
        speak = button_cols[0].button(
            "🎤 Voice",
            key=f"speak_user{user_number}",
            help="Click to use voice input"
        )
        send = button_cols[1].button(
            "Send",
            key=f"send_user{user_number}",
            help="Click to send message"
        )

        if speak:
            text = recognize_speech(LANGUAGE_OPTIONS[user_lang])
            if text:
                translated = translate_text(text, LANGUAGE_OPTIONS[user_lang], LANGUAGE_OPTIONS[target_lang])
                audio_file = text_to_speech(translated, LANGUAGE_OPTIONS[target_lang]) if translated else None
                if add_message_to_history(f"user{user_number}", text, translated, audio_file):
                    return True

        if send and text_input:
            translated = translate_text(text_input, LANGUAGE_OPTIONS[user_lang], LANGUAGE_OPTIONS[target_lang])
            audio_file = text_to_speech(translated, LANGUAGE_OPTIONS[target_lang]) if translated else None
            if add_message_to_history(f"user{user_number}", text_input, translated, audio_file):
                return True

    return False

def main():
    st.title("🌐 Multilingual Chat Translator Pro")
    st.markdown("### Connect Across Languages - Real-time Translation & Voice Chat")

    # Sidebar with enhanced styling
    with st.sidebar:
        st.markdown("""
            <h3 style='color: #1976D2; margin-bottom: 20px;'>🌍 Language Settings</h3>
        """, unsafe_allow_html=True)

        user1_lang = st.selectbox(
            "User 1 Language",
            list(LANGUAGE_OPTIONS.keys()),
            key="user1_lang",
            help="Select the language for User 1"
        )

        user2_lang = st.selectbox(
            "User 2 Language",
            [lang for lang in LANGUAGE_OPTIONS.keys() if lang != user1_lang],
            key="user2_lang",
            help="Select the language for User 2 (must be different from User 1)"
        )

        if st.button("🚸 Clear Chat History", help="Click to clear all chat messages"):
            st.session_state.chat_history = []
            for file in os.listdir():
                if file.startswith("audio_") and file.endswith(".mp3"):
                    try:
                        os.remove(file)
                    except Exception as e:
                        st.warning(f"Could not remove audio file: {str(e)}")
            st.experimental_rerun()

    # Chat interface
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
            <h3 style='color: #ff9800;'>User 1 ({user1_lang})</h3>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <h3 style='color: #4caf50;'>User 2 ({user2_lang})</h3>
        """, unsafe_allow_html=True)

    # Display messages
    user1_messages = col1.container()
    user2_messages = col2.container()

    for msg in st.session_state.chat_history:
        if msg["user"] == "user1":
            display_message(msg, user1_messages)
        else:
            display_message(msg, user2_messages)

    st.markdown("<br>", unsafe_allow_html=True)

    # Input sections
    input_col1, input_col2 = st.columns(2)

    if handle_user_input(1, user1_lang, user2_lang, input_col1):
        st.experimental_rerun()
    if handle_user_input(2, user2_lang, user1_lang, input_col2):
        st.experimental_rerun()

if __name__ == "__main__":
    main()
