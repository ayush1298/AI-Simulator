import tempfile
import streamlit as st
from pydub import AudioSegment, silence
import speech_recognition as sr
import os
from pathlib import Path

# Initialize recognizer
recog = sr.Recognizer()

def transcribe_audio(audio):
    """
    Transcribes audio from either uploaded file or recorded audio.
    
    Args:
        audio: Either a file-like object from st.file_uploader or bytes from st.audio_input
    
    Returns:
        tuple: (final_transcribed_text, chunk_results_list)
    """
    final_result = ""
    chunk_results = []
    
    try:
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded file to temporary location
            temp_audio_path = os.path.join(temp_dir, "uploaded_audio")
            
            # Handle different audio input types
            if hasattr(audio, 'getbuffer'):
                # File upload case
                with open(temp_audio_path, "wb") as f:
                    f.write(audio.getbuffer())
            else:
                # Audio recording case (bytes)
                with open(temp_audio_path, "wb") as f:
                    f.write(audio)
            
            # Load audio segment
            audio_segment = AudioSegment.from_file(temp_audio_path)
            
            # Split audio on silence
            chunks = silence.split_on_silence(
                audio_segment, 
                min_silence_len=500, 
                silence_thresh=audio_segment.dBFS-20, 
                keep_silence=100
            )
            
            if not chunks:
                # If no chunks found, use the entire audio
                chunks = [audio_segment]
            
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
                        chunk_results.append({
                            "chunk": index + 1,
                            "text": text,
                            "status": "success"
                        })
                    except sr.UnknownValueError:
                        final_result = final_result + " [Unaudible]"
                        chunk_results.append({
                            "chunk": index + 1,
                            "text": "[Unaudible]",
                            "status": "warning"
                        })
                    except sr.RequestError as e:
                        final_result = final_result + " [Recognition Error]"
                        chunk_results.append({
                            "chunk": index + 1,
                            "text": f"[Recognition Error: {e}]",
                            "status": "error"
                        })
                
                # Update progress
                progress_bar.progress((index + 1) / len(chunks))
            
            status_text.text("Transcription completed!")
            
    except Exception as e:
        st.error(f"An error occurred during processing: {str(e)}")
        final_result = "Error occurred during transcription"
        chunk_results.append({
            "chunk": "Error",
            "text": f"Error occurred during transcription: {str(e)}",
            "status": "error"
        })
    
    return final_result.strip(), chunk_results