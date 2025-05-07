import boto3
import time
import language_tool_python
import json
import requests
import os

def create_transcribe_client(region_name='eu-west-1'):
    return boto3.client('transcribe', region_name=region_name)

def upload_file_to_s3(bucket_name, file_path, object_name):
    s3 = boto3.client('s3')
    try:
        s3.upload_file(file_path, bucket_name, object_name)
        print(f" File uploaded to S3: s3://{bucket_name}/{object_name}")
    except Exception as e:
        print(f" Failed to upload file: {e}")

def start_transcription_job(transcribe_client, bucket_name, object_name, job_name, language_code='en-IN'):
    try:
        response = transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': f's3://{bucket_name}/{object_name}'},
            MediaFormat='wav',
            LanguageCode=language_code
        )
        print(f" Transcription job '{job_name}' started.")
        return response
    except Exception as e:
        print(f" Failed to start transcription job: {e}")
        return None

def get_transcription_result(transcribe_client, job_name):
    while True:
        response = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
        status = response['TranscriptionJob']['TranscriptionJobStatus']
        print(f" Job status: {status}")
        if status in ['COMPLETED', 'FAILED']:
            return response
        time.sleep(5)

if __name__ == "__main__":
    bucket_name = 'gaurav-transcribe-bucket'
    file_path = r'C:\Users\gaura\Downloads\WhatsApp-Audio-2025-04-07-at-22.19.07_e0824641.waptt.wav'
    object_name = 'WhatsApp-Audio-2025-04-07-at-22.19.07_e0824641.waptt.wav'
    job_name = f"grammar_transcribe_{int(time.time())}"
    language_code = 'en-IN'

    transcribe_client = create_transcribe_client()

    upload_file_to_s3(bucket_name, file_path, object_name)

    response = start_transcription_job(transcribe_client, bucket_name, object_name, job_name, language_code)

    if response:
        result = get_transcription_result(transcribe_client, job_name)

        if result['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
            transcript_url = result['TranscriptionJob']['Transcript']['TranscriptFileUri']
            print(f" Transcription completed successfully. Download URL:\n{transcript_url}")

            #  DOWNLOAD the transcript JSON
            transcript_json = requests.get(transcript_url).json()

            #  Extract the text
            transcript_text = transcript_json['results']['transcripts'][0]['transcript']

            #  Initialize language tool
            tool = language_tool_python.LanguageTool('en-IN')

            # Grammar checking
            matches = tool.check(transcript_text)

            errors = len(matches)
            words = len(transcript_text.split())
            grammar_score = max(0, 100 - (errors / words) * 100)

            suggestions = []
            for match in matches:
                suggestions.append({
                    'Mistake': match.context,
                    'Message': match.message,
                    'Suggestion': match.replacements
                })

            corrected_text = tool.correct(transcript_text)

            #  Print the results
            print(f"\n Grammar Score: {grammar_score:.2f}/100\n")
            print("Suggestions:")
            for suggestion in suggestions:
                print(suggestion)

            print("\n Corrected Transcript:")
            print(corrected_text)

        else:
            print(f" Transcription job failed.")


