import google.generativeai as genai
from pathlib import Path
import streamlit as st
from googletrans import Translator
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure GenAI API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to initialize the model
def initialize_model():
    generation_config = {"temperature": 0.9}
    return genai.GenerativeModel("gemini-1.5-flash", generation_config=generation_config)

# Function to process the image and generate content based on prompts
def generate_content(model, image_path, prompts):
    image_part = {
        "mime_type": "image/jpeg",
        "data": image_path.read_bytes()
    }
    
    results = []
    for prompt_text in prompts:
        prompt_parts = [prompt_text, image_part]
        response = model.generate_content(prompt_parts)
        
        if response.candidates:
            candidate = response.candidates[0]
            if candidate.content and candidate.content.parts:
                text_part = candidate.content.parts[0]
                if text_part.text:
                    results.append(f"Prompt: {prompt_text}\nDescription:\n{text_part.text}\n")
                else:
                    results.append(f"Prompt: {prompt_text}\nDescription: No valid content generated.\n")
            else:
                results.append(f"Prompt: {prompt_text}\nDescription: No content parts found.\n")
        else:
            results.append(f"Prompt: {prompt_text}\nDescription: No candidates found.\n")
    
    return results

# Function to translate text into selected language
def translate_text(text, lang):
    translator = Translator()
    translation = translator.translate(text, dest=lang)
    return translation.text

# Streamlit app
def main():
    # Initialize session state for prompts and results
    if "prompts" not in st.session_state:
        st.session_state.prompts = ""
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
            
            # Initialize the model
            model = initialize_model()
            
            # Input for multiple prompts
            st.write("Enter prompts (one per line):")
            st.session_state.prompts = st.text_area("Prompts", value=st.session_state.prompts)
            
            # Button to generate content
            if st.button("Generate Description"):
                # Split prompts into a list
                prompts = [prompt.strip() for prompt in st.session_state.prompts.split('\n') if prompt.strip()]
                
                if prompts:
                    # Generate content based on the uploaded image and user prompts
                    image_path = Path("temp_image.jpg")
                    st.session_state.results = generate_content(model, image_path, prompts)
                    # Save to history
                    st.session_state.history.append({
                        "image": uploaded_file,
                        "results": st.session_state.results
                    })
                else:
                    st.write("Please enter at least one prompt.")
            
            # Optionally remove the temporary file
            Path("temp_image.jpg").unlink()
        
        # Display the uploaded image and previously generated results
        if st.session_state.uploaded_file and st.session_state.results:
            st.image(st.session_state.uploaded_file, caption='Uploaded Image.', use_column_width=True)
            st.write("Chat - ClariView:")
            for description in st.session_state.results:
                st.write(description)

                # Add translation buttons for Indian regional languages
                if st.button("Translate to Tamil", key=f"translate_tamil_{description}"):
                    tamil_translation = translate_text(description, 'ta')
                    st.write(f"Translation (Tamil): {tamil_translation}")
                
                if st.button("Translate to Telugu", key=f"translate_telugu_{description}"):
                    telugu_translation = translate_text(description, 'te')
                    st.write(f"Translation (Telugu): {telugu_translation}")
                
                if st.button("Translate to Malayalam", key=f"translate_malayalam_{description}"):
                    malayalam_translation = translate_text(description, 'ml')
                    st.write(f"Translation (Malayalam): {malayalam_translation}")
                
                if st.button("Translate to Kannada", key=f"translate_kannada_{description}"):
                    kannada_translation = translate_text(description, 'kn')
                    st.write(f"Translation (Kannada): {kannada_translation}")
                
                if st.button("Translate to Hindi", key=f"translate_hindi_{description}"):
                    hindi_translation = translate_text(description, 'hi')
                    st.write(f"Translation (Hindi): {hindi_translation}")

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
