import streamlit as st
import json
import io
import base64
import time
from typing import Optional, Tuple
import requests
import tempfile
import os
from pathlib import Path

# Mock implementations for IBM Watson services
# In production, you would use actual IBM Watson SDK

class MockWatsonxLLM:
    """Mock implementation of IBM Watsonx Granite LLM for tone adaptation"""
    
    @staticmethod
    def rewrite_text(text: str, tone: str) -> str:
        """Rewrite text with specified tone while preserving meaning"""
        
        tone_prompts = {
            "Neutral": "Rewrite the following text in a clear, balanced, and objective tone while preserving all original meaning and key information:",
            "Suspenseful": "Rewrite the following text with dramatic tension, mystery, and engaging suspense while preserving all original meaning and key information:",
            "Inspiring": "Rewrite the following text with an uplifting, motivational, and inspiring tone while preserving all original meaning and key information:"
        }
        
        # Simulate tone-adaptive rewriting based on the original text
        if tone == "Suspenseful":
            # Add suspenseful elements
            text = text.replace(".", "... ")
            text = text.replace("important", "crucial")
            text = text.replace("will", "shall")
            text = f"What lies ahead? {text} The answer may surprise you."
            
        elif tone == "Inspiring":
            # Add inspirational elements
            text = text.replace("can", "have the power to")
            text = text.replace("should", "are destined to")
            text = text.replace("difficult", "challenging yet conquerable")
            text = f"Imagine the possibilities: {text} Your journey begins now!"
            
        elif tone == "Neutral":
            # Clean, professional tone
            text = text.replace("!", ".")
            text = text.replace("amazing", "notable")
            text = text.replace("awesome", "effective")
            
        return text

class MockWatsonTTS:
    """Mock implementation of IBM Watson Text-to-Speech"""
    
    @staticmethod
    def synthesize(text: str, voice: str = "Lisa") -> bytes:
        """Convert text to speech and return audio bytes"""
        
        # In a real implementation, this would call IBM Watson TTS API
        # For demo purposes, we'll create a placeholder audio response
        
        # Simulate API delay
        time.sleep(1)
        
        # Return mock audio data (in real implementation, this would be actual audio)
        audio_data = b"MOCK_AUDIO_DATA_" + text[:50].encode() + b"_" + voice.encode()
        return base64.b64encode(audio_data)

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'original_text' not in st.session_state:
        st.session_state.original_text = ""
    if 'rewritten_text' not in st.session_state:
        st.session_state.rewritten_text = ""
    if 'selected_tone' not in st.session_state:
        st.session_state.selected_tone = "Neutral"
    if 'selected_voice' not in st.session_state:
        st.session_state.selected_voice = "Lisa"
    if 'audio_data' not in st.session_state:
        st.session_state.audio_data = None

def process_uploaded_file(uploaded_file) -> str:
    """Process uploaded text file and return content"""
    try:
        content = uploaded_file.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        return content.strip()
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return ""

def create_audio_player(audio_data: bytes, filename: str = "audiobook.mp3"):
    """Create audio player with download capability"""
    
    # Create download link
    b64_audio = base64.b64encode(audio_data).decode()
    href = f'<a href="data:audio/mp3;base64,{b64_audio}" download="{filename}">Download Audio File</a>'
    
    return href

def main():
    st.set_page_config(
        page_title="EchoVerse - AI Audiobook Creator",
        page_icon="🎧",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.title("🎧 EchoVerse")
    st.subheader("Transform Your Text into Expressive Audiobooks")
    st.markdown("---")
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Voice selection
        st.subheader("Voice Selection")
        voice_options = ["Lisa", "Michael", "Allison"]
        st.session_state.selected_voice = st.selectbox(
            "Choose a voice:",
            voice_options,
            index=voice_options.index(st.session_state.selected_voice)
        )
        
        # Tone selection
        st.subheader("Tone Adaptation")
        tone_options = ["Neutral", "Suspenseful", "Inspiring"]
        st.session_state.selected_tone = st.selectbox(
            "Select desired tone:",
            tone_options,
            index=tone_options.index(st.session_state.selected_tone)
        )
        
        # Tone descriptions
        tone_descriptions = {
            "Neutral": "📝 Clear, balanced, and objective narration",
            "Suspenseful": "🎭 Dramatic tension and engaging mystery",
            "Inspiring": "✨ Uplifting and motivational delivery"
        }
        st.info(tone_descriptions[st.session_state.selected_tone])
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📄 Input Text")
        
        # Text input methods
        input_method = st.radio(
            "Choose input method:",
            ["Paste Text", "Upload File"],
            horizontal=True
        )
        
        if input_method == "Paste Text":
            text_input = st.text_area(
                "Enter your text:",
                value=st.session_state.original_text,
                height=300,
                placeholder="Paste your text here to convert it into an audiobook..."
            )
            
            if text_input != st.session_state.original_text:
                st.session_state.original_text = text_input
                st.session_state.rewritten_text = ""
                st.session_state.audio_data = None
                
        else:
            uploaded_file = st.file_uploader(
                "Upload a text file:",
                type=['txt'],
                help="Upload a .txt file to convert to audiobook"
            )
            
            if uploaded_file is not None:
                file_content = process_uploaded_file(uploaded_file)
                if file_content and file_content != st.session_state.original_text:
                    st.session_state.original_text = file_content
                    st.session_state.rewritten_text = ""
                    st.session_state.audio_data = None
                    
                    # Display uploaded content
                    st.text_area(
                        "Uploaded content:",
                        value=st.session_state.original_text,
                        height=300,
                        disabled=True
                    )
    
    with col2:
        st.header("🎨 Tone-Adapted Text")
        
        if st.session_state.original_text:
            # Process button
            if st.button("🔄 Generate Tone-Adapted Version", type="primary"):
                with st.spinner(f"Rewriting text with {st.session_state.selected_tone} tone..."):
                    try:
                        llm = MockWatsonxLLM()
                        st.session_state.rewritten_text = llm.rewrite_text(
                            st.session_state.original_text,
                            st.session_state.selected_tone
                        )
                        st.success("Text successfully adapted!")
                    except Exception as e:
                        st.error(f"Error processing text: {str(e)}")
            
            # Display rewritten text
            if st.session_state.rewritten_text:
                st.text_area(
                    f"Text adapted for {st.session_state.selected_tone} tone:",
                    value=st.session_state.rewritten_text,
                    height=300,
                    disabled=True
                )
        else:
            st.info("👆 Please enter or upload text to begin")
    
    # Audio generation and playback section
    if st.session_state.rewritten_text:
        st.markdown("---")
        st.header("🎵 Audio Generation")
        
        col3, col4 = st.columns([1, 1])
        
        with col3:
            if st.button("🎤 Generate Audio", type="primary"):
                with st.spinner(f"Converting to speech with {st.session_state.selected_voice} voice..."):
                    try:
                        tts = MockWatsonTTS()
                        audio_bytes = tts.synthesize(
                            st.session_state.rewritten_text,
                            st.session_state.selected_voice
                        )
                        st.session_state.audio_data = audio_bytes
                        st.success("Audio generated successfully!")
                    except Exception as e:
                        st.error(f"Error generating audio: {str(e)}")
        
        with col4:
            if st.session_state.audio_data:
                st.subheader("🎧 Your Audiobook")
                
                # In a real implementation, you would use st.audio() with actual audio data
                st.info("🎵 Audio preview would be available here")
                st.caption(f"Voice: {st.session_state.selected_voice} | Tone: {st.session_state.selected_tone}")
                
                # Download link
                filename = f"audiobook_{st.session_state.selected_tone.lower()}_{st.session_state.selected_voice.lower()}.mp3"
                
                # Mock download button (in real implementation, use actual audio data)
                if st.download_button(
                    label="📥 Download Audio File",
                    data=base64.b64decode(st.session_state.audio_data),
                    file_name=filename,
                    mime="audio/mp3"
                ):
                    st.success("Download started!")
    
    # Text comparison section
    if st.session_state.original_text and st.session_state.rewritten_text:
        st.markdown("---")
        st.header("📊 Side-by-Side Comparison")
        
        comparison_col1, comparison_col2 = st.columns([1, 1])
        
        with comparison_col1:
            st.subheader("📄 Original Text")
            st.text_area(
                "Original:",
                value=st.session_state.original_text,
                height=200,
                disabled=True,
                key="original_comparison"
            )
            
            # Text statistics
            original_stats = {
                "Words": len(st.session_state.original_text.split()),
                "Characters": len(st.session_state.original_text),
                "Estimated reading time": f"{len(st.session_state.original_text.split()) // 200 + 1} min"
            }
            
            for stat, value in original_stats.items():
                st.metric(stat, value)
        
        with comparison_col2:
            st.subheader(f"🎨 {st.session_state.selected_tone} Version")
            st.text_area(
                f"{st.session_state.selected_tone} adaptation:",
                value=st.session_state.rewritten_text,
                height=200,
                disabled=True,
                key="rewritten_comparison"
            )
            
            # Adapted text statistics
            adapted_stats = {
                "Words": len(st.session_state.rewritten_text.split()),
                "Characters": len(st.session_state.rewritten_text),
                "Estimated reading time": f"{len(st.session_state.rewritten_text.split()) // 200 + 1} min"
            }
            
            for stat, value in adapted_stats.items():
                st.metric(stat, value)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>🎧 EchoVerse - Powered by IBM Watson AI | Making content accessible through AI-driven audiobook creation</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()