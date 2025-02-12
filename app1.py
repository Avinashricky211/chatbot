import streamlit as st
from together import Together
import base64
import io
from PIL import Image
import docx
import os
import PyPDF2

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
        Extract text from various document types
        """
        try:
            # PDF extraction using PyPDF2
            if uploaded_file.type == 'application/pdf':
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
            
            # Word document extraction
            elif uploaded_file.type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                temp_path = "temp_document.docx"
                with open(temp_path, "wb") as temp_file:
                    temp_file.write(uploaded_file.getvalue())
                
                doc = docx.Document(temp_path)
                full_text = "\n".join([para.text for para in doc.paragraphs])
                os.remove(temp_path)
                return full_text
            
            # Plain text
            else:
                return uploaded_file.getvalue().decode('utf-8')
        
        except Exception as e:
            st.error(f"Error extracting text: {e}")
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
        page_title="Document Analysis Chatbot",
        page_icon=":robot:",
        layout="centered"
    )
    
    st.title("Revenue Document Analysis Bot 🤖")
    
    # API Configuration in main section
    with st.expander("Click This to Enter Your Secret Key", expanded=False):
        api_key = st.text_input("Enter Your Secret Key", type="password")
    
    if not api_key:
        st.warning("")
        st.stop()
    
    try:
        chatbot = LlamaVisionChatbot(api_key=api_key)
        
        # Task Selection
        app_mode = st.selectbox(
            "Choose Your Task", 
            ["Document Q&A", "Text Summarization", "Translation"]
        )
        
        # File Upload
        st.subheader("Upload Document")
        col1, col2 = st.columns([3, 1])
        with col1:
            uploaded_file = st.file_uploader(
                "Choose a file", 
                type=['pdf', 'docx', 'txt'],
                help="Supported formats: PDF, Word, Text"
            )
        
        if uploaded_file is not None:
            # Show file details
            with col2:
                st.write("File Info:")
                st.write(f"Size: {uploaded_file.size/1024:.1f} KB")
            
            extracted_text = chatbot.extract_text_from_document(uploaded_file)
            
            # Document Q&A
            if app_mode == "Document Q&A":
                st.subheader("Ask Questions")
                user_question = st.text_input("What would you like to know about the document?")
                
                if st.button("Get Answer", type="primary", use_container_width=True) and user_question:
                    with st.spinner("Processing your question..."):
                        answer = chatbot.chat_with_model(extracted_text, user_question)
                        if answer:
                            st.success("Answer:")
                            st.write(answer)
                            download_button = chatbot.download_content(answer, "qa_response")
                            st.markdown(download_button, unsafe_allow_html=True)
            
            # Text Summarization
            elif app_mode == "Text Summarization":
                st.subheader("Document Summary")
                if st.button("Generate Summary", type="primary", use_container_width=True):
                    with st.spinner("Generating summary..."):
                        summary = chatbot.summarize_text(extracted_text)
                        if summary:
                            st.success("Summary:")
                            st.write(summary)
                            download_button = chatbot.download_content(summary, "document_summary")
                            st.markdown(download_button, unsafe_allow_html=True)
            
            # Translation
            elif app_mode == "Translation":
                st.subheader("Translation")
                target_language = st.selectbox(
                    "Select Target Language",
                    ["Telugu", "Spanish", "French", "German", "Chinese"]
                )
                
                if st.button("Translate Document", type="primary", use_container_width=True):
                    with st.spinner(f"Translating to {target_language}..."):
                        translation = chatbot.translate_text(extracted_text, target_language)
                        if translation:
                            st.success(f"Translation ({target_language}):")
                            st.write(translation)
                            download_button = chatbot.download_content(
                                translation,
                                f"{target_language.lower()}_translation"
                            )
                            st.markdown(download_button, unsafe_allow_html=True)
                    
        # Footer
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center'>Powered by Revenue</div>",
            unsafe_allow_html=True
        )
    
    except Exception as e:
        st.error(f"Application Error: {e}")

if __name__ == "__main__":
    main()