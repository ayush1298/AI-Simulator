import streamlit as st
from pydub import AudioSegment, silence
import speech_recognition as sr
import os
import tempfile
from pathlib import Path

# Initialize recognizer
recog = sr.Recognizer()

st.markdown("<h1 style='text-align: center;'>Audio To Text Converter</h1>", unsafe_allow_html=True)
st.markdown("---", unsafe_allow_html=True)

# File uploader
audio = st.file_uploader("Upload Your Audio File", type=['mp3', 'wav'])

if audio:
    # Display audio player
    st.audio(audio)
    
    # Add a button to start transcription
    if st.button("Start Transcription", type="primary"):
        with st.spinner("Processing audio file..."):
            final_result = ""
            
            try:
                # Create temporary directory for processing
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Save uploaded file to temporary location
                    temp_audio_path = os.path.join(temp_dir, "uploaded_audio")
                    with open(temp_audio_path, "wb") as f:
                        f.write(audio.getbuffer())
                    
                    # Load audio segment
                    audio_segment = AudioSegment.from_file(temp_audio_path)
                    
                    # Split audio on silence
                    chunks = silence.split_on_silence(
                        audio_segment, 
                        min_silence_len=500, 
                        silence_thresh=audio_segment.dBFS-20, 
                        keep_silence=100
                    )
                    
                    # Process each chunk
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for index, chunk in enumerate(chunks):
                        status_text.text(f"Processing chunk {index + 1} of {len(chunks)}...")
                        
                        # Export chunk to temporary file
                        chunk_path = os.path.join(temp_dir, f"chunk_{index}.wav")
                        chunk.export(chunk_path, format="wav")
                        
                        # Transcribe chunk
                        with sr.AudioFile(chunk_path) as source:
                            recorded = recog.record(source)
                            try:
                                text = recog.recognize_google(recorded)
                                final_result = final_result + " " + text
                                st.success(f"Chunk {index + 1}: {text}")
                            except sr.UnknownValueError:
                                st.warning(f"Chunk {index + 1}: Could not understand audio")
                                final_result = final_result + " [Unaudible]"
                            except sr.RequestError as e:
                                st.error(f"Chunk {index + 1}: Error with speech recognition service: {e}")
                                final_result = final_result + " [Recognition Error]"
                        
                        # Update progress
                        progress_bar.progress((index + 1) / len(chunks))
                    
                    status_text.text("Transcription completed!")
                    
            except Exception as e:
                st.error(f"An error occurred during processing: {str(e)}")
                final_result = "Error occurred during transcription"
        
        # Display final result
        if final_result.strip():
            st.markdown("### 📝 Transcription Result")
            st.text_area(
                "Transcript", 
                value=final_result.strip(), 
                height=200,
                help="You can edit the transcript before downloading"
            )
            
            # Download section
            st.markdown("### 💾 Download Options")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📥 Download as TXT"):
                    downloads_path = str(Path.home() / "Downloads" / "transcript.txt")
                    with open(downloads_path, 'w', encoding='utf-8') as file:
                        file.write(final_result.strip())
                    st.success(f"✅ Transcript saved to {downloads_path}")
            
            with col2:
                # Provide download button that works in browser
                st.download_button(
                    label="📄 Download Transcript",
                    data=final_result.strip(),
                    file_name="transcript.txt",
                    mime="text/plain"
                )
    
    # Show instructions
    st.markdown("### 📋 Instructions")
    st.info("""
    1. Upload your audio file (MP3 or WAV format)
    2. Click 'Start Transcription' to begin processing
    3. Watch the real-time progress as each audio chunk is processed
    4. Review the transcription results in the text area
    5. Download the transcript using either download option
    """)

else:
    st.info("👆 Please upload an audio file to get started")
    
    # Show supported formats
    st.markdown("### 🎵 Supported Formats")
    st.markdown("- **MP3** - Most common audio format")
    st.markdown("- **WAV** - Uncompressed audio format")