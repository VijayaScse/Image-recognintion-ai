import google.generativeai as genai
from pathlib import Path
import streamlit as st
from googletrans import Translator
from gtts import gTTS
import io

# Configure GenAI API key
genai.configure(api_key="AIzaSyCtVvft0weDJWOxQRTLm_J7cWBKVy5LIhA")

def initialize_model():
    """Initialize the GenAI model."""
    generation_config = {"temperature": 0.9}
    return genai.GenerativeModel("gemini-1.5-flash", generation_config=generation_config)

def generate_content(model, image_path, questions):
    """Generate content based on the image and questions."""
    image_part = {
        "mime_type": "image/jpeg",
        "data": image_path.read_bytes()
    }
    results = []
    for question_text in questions:
        question_parts = [question_text, image_part]
        response = model.generate_content(question_parts)
        if response.candidates:
            candidate = response.candidates[0]
            text_part = candidate.content.parts[0] if candidate.content and candidate.content.parts else None
            results.append(f"Question: {question_text}\nDescription:\n{text_part.text if text_part and text_part.text else 'No valid content generated.'}\n")
        else:
            results.append(f"Question: {question_text}\nDescription: No candidates found.\n")
    return results

def translate_text(text, lang):
    """Translate text to the specified language."""
    translator = Translator()
    translation = translator.translate(text, dest=lang)
    return translation.text

def generate_audio(text, lang):
    """Generate audio from text in the specified language."""
    tts = gTTS(text, lang=lang)
    audio_bytes = io.BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    return audio_bytes

def main():
    """Main function to handle the Streamlit app."""
    if "questions" not in st.session_state:
        st.session_state.questions = ""
    if "results" not in st.session_state:
        st.session_state.results = []
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None
    if "history" not in st.session_state:
        st.session_state.history = []

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Chat: ClariView", "History"])

    if page == "Chat: ClariView":
        st.title("ClariView - Image Interpreter")
        uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            st.session_state.uploaded_file = uploaded_file
            with open("temp_image.jpg", "wb") as f:
                f.write(uploaded_file.getvalue())
            st.image(uploaded_file, caption='Uploaded Image.', use_column_width=True)
            
            model = initialize_model()
            st.write("Enter questions (one per line):")
            st.session_state.questions = st.text_area("Questions", value=st.session_state.questions)
            
            if st.button("Generate Description"):
                questions = [q.strip() for q in st.session_state.questions.split('\n') if q.strip()]
                if questions:
                    image_path = Path("temp_image.jpg")
                    st.session_state.results = generate_content(model, image_path, questions)
                    st.session_state.history.append({"image": uploaded_file, "results": st.session_state.results})
                else:
                    st.write("Please enter at least one question.")
            Path("temp_image.jpg").unlink()
        
        if st.session_state.results:
            st.write("Chat - ClariView:")
            for description in st.session_state.results:
                st.write(description)
                st.audio(generate_audio(description, 'en'), format="audio/mp3")

                # Translation and audio generation for Indian languages
                languages = {
                    "Tamil": "ta",
                    "Telugu": "te",
                    "Malayalam": "ml",
                    "Kannada": "kn",
                    "Hindi": "hi"
                }

                for lang_name, lang_code in languages.items():
                    if st.button(f"Translate to {lang_name}", key=f"{lang_name}_{description}"):
                        translation = translate_text(description, lang_code)
                        st.write(f"{lang_name} Translation: {translation}")
                        st.audio(generate_audio(translation, lang_code), format="audio/mp3")

    elif page == "History":
        st.title("History of Generated Descriptions")
        if st.session_state.history:
            for idx, entry in enumerate(st.session_state.history):
                st.write(f"Entry {idx+1}")
                st.image(entry["image"], caption=f'Image {idx+1}', use_column_width=True)
                for description in entry["results"]:
                    st.write(description)
        else:
            st.write("No history available yet.")

if __name__ == "__main__":
    main()
