import speech_recognition as sr
import streamlit as st
import io

def transcribe_audio(audio_file):
    """Converts recorded Streamlit audio file into text without crashing the UI player."""
    recognizer = sr.Recognizer()
    
    audio_bytes = audio_file.getvalue()
    isolated_audio = io.BytesIO(audio_bytes)
    
    with sr.AudioFile(isolated_audio) as source:
        audio_data = recognizer.record(source)
        
        try:
            with st.spinner("Transcribing... 📝"):
                # Transcribe using Indian English accent locale
                text = recognizer.recognize_google(audio_data, language="en-IN")
                return text
        except sr.UnknownValueError:
            st.warning("Samajh nahi aaya. Thoda clear bol.")
            return None
        except sr.RequestError as e:
            st.error(f"Speech service error: {e}")
            return None
