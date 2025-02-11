import streamlit as st
from together import Together
import base64
import io
from PIL import Image
import docx
import os

class LlamaVisionChatbot:
    def __init__(self, api_key):
        """
        Initialize the chatbot with Together API client
        """
        try:
            # Initialize Together client
            self.client = Together(api_key=api_key)
            
            # Define model paths
            self.vision_model = "meta-llama/Llama-Vision-Free"
            self.chat_model = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
        
        except Exception as e:
            st.error(f"Initialization Error: {e}")
    
    def extract_text_from_document(self, uploaded_file):
        """
        Extract text from various document types using Llama Vision Model
        """
        try:
            # PDF extraction
            if uploaded_file.type == 'application/pdf':
                from pdf2image import convert_from_bytes
                images = convert_from_bytes(uploaded_file.getvalue(), first_page=1, last_page=1)
                image = images[0]
                return self._process_image_to_text(image)
            
            # Word document extraction
            elif uploaded_file.type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                temp_path = "temp_document.docx"
                with open(temp_path, "wb") as temp_file:
                    temp_file.write(uploaded_file.getvalue())
                
                doc = docx.Document(temp_path)
                full_text = "\n".join([para.text for para in doc.paragraphs])
                os.remove(temp_path)
                return full_text
            
            # Image extraction
            elif uploaded_file.type.startswith('image/'):
                image = Image.open(uploaded_file)
                return self._process_image_to_text(image)
            
            # Plain text
            else:
                return uploaded_file.getvalue().decode('utf-8')
        
        except Exception as e:
            st.error(f"Error extracting text: {e}")
            return None
    
    def _process_image_to_text(self, image):
        """
        Helper method to process image to text using Vision Model
        """
        try:
            # Convert PIL Image to base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            # Prepare messages for Vision Model
            messages = [
                {
                    "role": "user", 
                    "content": "Describe the contents of this image in detail, extracting all readable text. "
                               "Provide a comprehensive text description."
                },
                {
                    "role": "user", 
                    "content": [
                        {
                            "type": "image_url", 
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=messages
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            st.error(f"Vision Model Processing Error: {e}")
            return None
    
    def process_with_vision_model(self, image=None, text=None):
        """
        Process image with Vision Model
        """
        try:
            # Extract text from image
            image_text = self._process_image_to_text(image)
            
            # If additional text is provided, combine it
            if text:
                full_description = f"{text}\n\nImage Contents:\n{image_text}"
            else:
                full_description = image_text
            
            return full_description
        
        except Exception as e:
            st.error(f"Vision Model Processing Error: {e}")
            return None

    def chat_with_model(self, context, question):
        """
        Generate response using Chat Model
        """
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant who answers questions based on the given context."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
            ]
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"Chat Model Processing Error: {e}")
            return None

    def summarize_text(self, text):
        """
        Generate summary of text
        """
        try:
            messages = [
                {"role": "system", "content": "You are an expert summarizer. Provide a concise and clear summary of the following text."},
                {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
            ]
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"Summarization Error: {e}")
            return None

    def translate_text(self, text, target_language='Spanish'):
        """
        Translate text to target language
        """
        try:
            messages = [
                {"role": "system", "content": f"You are a professional translator. Translate the text to {target_language}."},
                {"role": "user", "content": f"Translate the following text to {target_language}:\n\n{text}"}
            ]
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"Translation Error: {e}")
            return None

    def download_content(self, content, filename, file_type='txt'):
        """
        Create downloadable content
        """
        try:
            if file_type == 'txt':
                b64 = base64.b64encode(content.encode()).decode()
                href = f'<a href="data:file/txt;base64,{b64}" download="{filename}.txt">Download {filename}.txt</a>'
                return href
        except Exception as e:
            st.error(f"Download Error: {e}")
            return None

def main():
    st.set_page_config(
        page_title="Llama Vision Chatbot", 
        page_icon=":robot:", 
        layout="wide"
    )
    
    st.sidebar.title("Together API Configuration")
    api_key = st.sidebar.text_input("Enter Your Together API Key", type="password")
    
    if api_key:
        try:
            chatbot = LlamaVisionChatbot(api_key=api_key)
            
            st.sidebar.title("Navigation")
            app_mode = st.sidebar.selectbox(
                "Choose Your Task", 
                ["Document Q&A", "Text Summarization", "Translation", "Vision Processing"]
            )
            
            st.title("Avinash Vision Chatbot 🤖")
            st.sidebar.header("Upload Document")
            uploaded_file = st.sidebar.file_uploader("Choose a file", type=['pdf', 'docx', 'txt', 'png', 'jpg'])
            
            if uploaded_file is not None:
                extracted_text = chatbot.extract_text_from_document(uploaded_file)
                
                if app_mode == "Document Q&A":
                    st.subheader("Document Question & Answer")
                    user_question = st.text_input("Ask a question about the document")
                    
                    if st.button("Get Answer") and user_question:
                        answer = chatbot.chat_with_model(extracted_text, user_question)
                        st.write("Answer:", answer)
                        if answer:
                            download_button = chatbot.download_content(answer, "qa_response")
                            st.markdown(download_button, unsafe_allow_html=True)
                
                elif app_mode == "Text Summarization":
                    st.subheader("Document Summarization")
                    
                    if st.button("Summarize Document"):
                        summary = chatbot.summarize_text(extracted_text)
                        st.write("Summary:", summary)
                        if summary:
                            download_button = chatbot.download_content(summary, "document_summary")
                            st.markdown(download_button, unsafe_allow_html=True)
                
                elif app_mode == "Translation":
                    st.subheader("Document Translation")
                    target_language = st.selectbox("Select Target Language", ["Spanish", "French", "German", "Chinese", "Telugu"])
                    
                    if st.button("Translate"):
                        translation = chatbot.translate_text(extracted_text, target_language)
                        st.write(f"Translation to {target_language}:", translation)
                        if translation:
                            download_button = chatbot.download_content(translation, f"{target_language.lower()}_translation")
                            st.markdown(download_button, unsafe_allow_html=True)
                
                elif app_mode == "Vision Processing":
                    st.subheader("Image Processing")
                    if uploaded_file.type.startswith('image/'):
                        image = Image.open(uploaded_file)
                        st.image(image, caption='Uploaded Image', use_column_width=True)
                        
                        description = st.text_input("Optional description for image")
                        
                        if st.button("Process Image"):
                            result = chatbot.process_with_vision_model(image=image, text=description)
                            st.write("Vision Model Output:", result)
                            if result:
                                download_button = chatbot.download_content(result, "vision_output")
                                st.markdown(download_button, unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"Initialization Error: {e}")
    
    st.sidebar.markdown("---")
    st.sidebar.info("Powered by Avinash")

if __name__ == "__main__":
    main()
