import google.generativeai as genai
from pathlib import Path
import streamlit as st
from googletrans import Translator
from gtts import gTTS
import io

# Configure GenAI API key
genai.configure(api_key="AIzaSyCtVvft0weDJWOxQRTLm_J7cWBKVy5LIhA")

# Function to initialize the model
def initialize_model():
    generation_config = {"temperature": 0.9}
    return genai.GenerativeModel("gemini-1.5-flash", generation_config=generation_config)

# Function to process the image and generate content based on questions
def generate_content(model, image_path, questions):
    image_part = {
        "mime_type": "image/jpeg",
        "data": image_path.read_bytes()
    }
    
    results = []
    for question_text in questions:
        question_parts = [question_text, image_part]
        response = model.generate_content(question_parts)
        
        # Extract and return the text content from the response
        if response.candidates:
            candidate = response.candidates[0]
            if candidate.content and candidate.content.parts:
                text_part = candidate.content.parts[0]
                if text_part.text:
                    results.append(f"Question: {question_text}\nDescription:\n{text_part.text}\n")
                else:
                    results.append(f"Question: {question_text}\nDescription: No valid content generated.\n")
            else:
                results.append(f"Question: {question_text}\nDescription: No content parts found.\n")
        else:
            results.append(f"Question: {question_text}\nDescription: No candidates found.\n")
    
    return results

# Function to translate text into a selected language
def translate_text(text, lang):
    translator = Translator()
    translation = translator.translate(text, dest=lang)
    return translation.text

# Function to generate audio from text
def generate_audio(text, lang):
    tts = gTTS(text, lang=lang)
    audio_bytes = io.BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    return audio_bytes

# Streamlit app
def main():
    # Initialize session state for questions and results
    if "questions" not in st.session_state:
        st.session_state.questions = ""
    if "results" not in st.session_state:
        st.session_state.results = []
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None
    if "history" not in st.session_state:
        st.session_state.history = []

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Chat: ClariView", "History"])

    if page == "Chat: ClariView":
        st.title("ClariView - Image Interpreter")

        # Upload an image file
        uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            st.session_state.uploaded_file = uploaded_file
            # Save the uploaded file
            with open("temp_image.jpg", "wb") as f:
                f.write(uploaded_file.getvalue())

            # Display the uploaded image immediately
            st.image(uploaded_file, caption='Uploaded Image.', use_column_width=True)
            
            # Initialize the model
            model = initialize_model()
            
            # Input for multiple questions
            st.write("Enter questions (one per line):")
            st.session_state.questions = st.text_area("Questions", value=st.session_state.questions)
            
            # Button to generate content
            if st.button("Generate Description"):
                # Split questions into a list
                questions = [question.strip() for question in st.session_state.questions.split('\n') if question.strip()]
                
                if questions:
                    # Generate content based on the uploaded image and user questions
                    image_path = Path("temp_image.jpg")
                    st.session_state.results = generate_content(model, image_path, questions)
                    # Save to history
                    st.session_state.history.append({
                        "image": uploaded_file,
                        "results": st.session_state.results
                    })
                else:
                    st.write("Please enter at least one question.")
            
            # Optionally remove the temporary file
            Path("temp_image.jpg").unlink()
        
        # Display previously generated results
        if st.session_state.results:
            st.write("Chat - ClariView:")
            for description in st.session_state.results:
                st.write(description)

                # Generate and play default English audio
                english_audio = generate_audio(description, 'en')
                st.audio(english_audio, format="audio/mp3")

                # Add translation buttons with audio for Indian regional languages
                if st.button("Translate to Tamil", key=f"translate_tamil_{description}"):
                    tamil_translation = translate_text(description, 'ta')
                    st.write(tamil_translation)
                    tamil_audio = generate_audio(tamil_translation, 'ta')
                    st.audio(tamil_audio, format="audio/mp3")
                
                if st.button("Translate to Telugu", key=f"translate_telugu_{description}"):
                    telugu_translation = translate_text(description, 'te')
                    st.write(telugu_translation)
                    telugu_audio = generate_audio(telugu_translation, 'te')
                    st.audio(telugu_audio, format="audio/mp3")
                
                if st.button("Translate to Malayalam", key=f"translate_malayalam_{description}"):
                    malayalam_translation = translate_text(description, 'ml')
                    st.write(malayalam_translation)
                    malayalam_audio = generate_audio(malayalam_translation, 'ml')
                    st.audio(malayalam_audio, format="audio/mp3")
                
                if st.button("Translate to Kannada", key=f"translate_kannada_{description}"):
                    kannada_translation = translate_text(description, 'kn')
                    st.write(kannada_translation)
                    kannada_audio = generate_audio(kannada_translation, 'kn')
                    st.audio(kannada_audio, format="audio/mp3")
                
                if st.button("Translate to Hindi", key=f"translate_hindi_{description}"):
                    hindi_translation = translate_text(description, 'hi')
                    st.write(hindi_translation)
                    hindi_audio = generate_audio(hindi_translation, 'hi')
                    st.audio(hindi_audio, format="audio/mp3")

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
