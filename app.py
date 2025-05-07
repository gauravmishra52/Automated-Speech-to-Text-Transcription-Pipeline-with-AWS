import streamlit as st
import requests
from transcribe_aws import upload_to_s3, start_transcription_job, get_transcription_text
from grammar_check import grammar_score
import os

st.set_page_config(page_title="Grammar AI Engine", layout="centered")
st.title("📢 Grammar AI: Audio Grammar Analysis")

BUCKET_NAME = 'your-s3-bucket-name'  # Replace with your bucket

uploaded_file = st.file_uploader("🎧 Upload Audio File", type=["wav", "mp3", "mp4"])

if uploaded_file:
    os.makedirs("audio_uploads", exist_ok=True)
    file_path = f"audio_uploads/{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("File uploaded ✅")

    s3_uri = upload_to_s3(file_path, BUCKET_NAME, uploaded_file.name)
    job_name = uploaded_file.name.split('.')[0]
    start_transcription_job(job_name, s3_uri, BUCKET_NAME)

    st.info("⏳ Transcription in progress...")
    transcript_uri = get_transcription_text(job_name)
    transcript_data = requests.get(transcript_uri).json()
    text = transcript_data['results']['transcripts'][0]['transcript']

    st.text_area("📝 Transcribed Text", text, height=200)

    score, mistakes, corrected = grammar_score(text)
    st.metric("🧠 Grammar Score", f"{score}%")
    st.subheader("✍️ Mistakes & Suggestions")
    for mistake, correction in mistakes:
        st.write(f"**{mistake}** ➜ **{correction}**")

    st.subheader("✅ Corrected Text")
    st.write(corrected)
