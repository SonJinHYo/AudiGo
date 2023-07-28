from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import exceptions

from . import serializers
from .models import Audio

import environ
import os
from django.conf import settings

import boto3
import time
import uuid
import requests
import json
import openai


class Scripts(APIView):
    permission_classes = [IsAuthenticated]

    def get_objects(self, pk, user):
        try:
            return Audio.objects.get(pk=pk, user=user)
        except:
            raise exceptions.NotFound

    def get(self, pk, request):
        audio = self.get_objects(pk, request.user)
        serializer = serializers.DetailAudioSerializer(audio)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class UploadAudio(APIView):
    permission_classes = [IsAuthenticated]

    env = environ.Env()
    environ.Env.read_env(os.path.join(settings.BASE_DIR, ".env"))

    s3 = boto3.client(
        "s3",
        aws_access_key_id=env("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=env("AWS_SECRET_ACCESS_KEY"),
    )

    transcript = boto3.client(
        "transcribe",
        aws_access_key_id=env("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=env("AWS_SECRET_ACCESS_KEY"),
    )
    openai.api_key = env("TEST_KEY")

    def post(self, request):
        # 이후 오디오 파일 크기 제한 걸기
        user = request.user
        audio_file = request.FILES.get("audio_file")
        title = request.data["title"]
        bucket = self.env("BUCKET")
        key = f"{str(uuid.uuid4())}__{audio_file}"
        job_name = bucket + key

        self.s3.upload_file(
            Filename=title,
            bucket=bucket,
            key=key,
        )

        def get_script(job_name: str) -> tuple(str, dict):
            # transcript 작업 완료 대기
            max_tries = 60
            while max_tries > 0:
                max_tries -= 1
                job = self.transcript.get_transcription_job(
                    TranscriptionJobName=job_name
                )
                job_status = job["TranscriptionJob"]["TranscriptionJobStatus"]
                if job_status in ["COMPLETED", "FAILED"]:
                    print(f"Job {job_name} is {job_status}.")
                    if job_status == "COMPLETED":
                        print(
                            f"Download the transcript from\n"
                            f"\t{job['TranscriptionJob']['Transcript']['TranscriptFileUri']}."
                        )
                    break
                else:
                    print(f"Waiting for {job_name}. Current status is {job_status}.")
                time.sleep(10)

            print("transcript finished..!")
            print("trying analytics job...")
            response = self.transcript.get_transcription_job(
                TranscriptionJobName=job_name
            )
            """response syntex
            {
                'TranscriptionJob': {
                    'TranscriptionJobName': 'string',
                    'TranscriptionJobStatus': 'QUEUED'|'IN_PROGRESS'|'FAILED'|'COMPLETED',
                    'LanguageCode': 'af-ZA'|'ar-AE'|'ar-SA'|'da-DK'|'de-CH'|'de-DE'|'en-AB'|'en-AU'|'en-GB'|'en-IE'|'en-IN'|'en-US'|'en-WL'|'es-ES'|'es-US'|'fa-IR'|'fr-CA'|'fr-FR'|'he-IL'|'hi-IN'|'id-ID'|'it-IT'|'ja-JP'|'ko-KR'|'ms-MY'|'nl-NL'|'pt-BR'|'pt-PT'|'ru-RU'|'ta-IN'|'te-IN'|'tr-TR'|'zh-CN'|'zh-TW'|'th-TH'|'en-ZA'|'en-NZ'|'vi-VN'|'sv-SE',
                    'MediaSampleRateHertz': 123,
                    'MediaFormat': 'mp3'|'mp4'|'wav'|'flac'|'ogg'|'amr'|'webm',
                    'Media': {
                        'MediaFileUri': 'string',
                        'RedactedMediaFileUri': 'string'
                    },
                    'Transcript': {
                        'TranscriptFileUri': 'string',
                        'RedactedTranscriptFileUri': 'string'
                    },
                    'StartTime': datetime(2015, 1, 1),
                    'CreationTime': datetime(2015, 1, 1),
                    'CompletionTime': datetime(2015, 1, 1),
                    'FailureReason': 'string',
                    'Settings': {
                        'VocabularyName': 'string',
                        'ShowSpeakerLabels': True|False,
                        'MaxSpeakerLabels': 123,
                        'ChannelIdentification': True|False,
                        'ShowAlternatives': True|False,
                        'MaxAlternatives': 123,
                        'VocabularyFilterName': 'string',
                        'VocabularyFilterMethod': 'remove'|'mask'|'tag'
                    },
                    'ModelSettings': {
                        'LanguageModelName': 'string'
                    },
                    'JobExecutionSettings': {
                        'AllowDeferredExecution': True|False,
                        'DataAccessRoleArn': 'string'
                    },
                    'ContentRedaction': {
                        'RedactionType': 'PII',
                        'RedactionOutput': 'redacted'|'redacted_and_unredacted',
                        'PiiEntityTypes': [
                            'BANK_ACCOUNT_NUMBER'|'BANK_ROUTING'|'CREDIT_DEBIT_NUMBER'|'CREDIT_DEBIT_CVV'|'CREDIT_DEBIT_EXPIRY'|'PIN'|'EMAIL'|'ADDRESS'|'NAME'|'PHONE'|'SSN'|'ALL',
                        ]
                    },
                    'IdentifyLanguage': True|False,
                    'IdentifyMultipleLanguages': True|False,
                    'LanguageOptions': [
                        'af-ZA'|'ar-AE'|'ar-SA'|'da-DK'|'de-CH'|'de-DE'|'en-AB'|'en-AU'|'en-GB'|'en-IE'|'en-IN'|'en-US'|'en-WL'|'es-ES'|'es-US'|'fa-IR'|'fr-CA'|'fr-FR'|'he-IL'|'hi-IN'|'id-ID'|'it-IT'|'ja-JP'|'ko-KR'|'ms-MY'|'nl-NL'|'pt-BR'|'pt-PT'|'ru-RU'|'ta-IN'|'te-IN'|'tr-TR'|'zh-CN'|'zh-TW'|'th-TH'|'en-ZA'|'en-NZ'|'vi-VN'|'sv-SE',
                    ],
                    'IdentifiedLanguageScore': ...,
                    'LanguageCodes': [
                        {
                            'LanguageCode': 'af-ZA'|'ar-AE'|'ar-SA'|'da-DK'|'de-CH'|'de-DE'|'en-AB'|'en-AU'|'en-GB'|'en-IE'|'en-IN'|'en-US'|'en-WL'|'es-ES'|'es-US'|'fa-IR'|'fr-CA'|'fr-FR'|'he-IL'|'hi-IN'|'id-ID'|'it-IT'|'ja-JP'|'ko-KR'|'ms-MY'|'nl-NL'|'pt-BR'|'pt-PT'|'ru-RU'|'ta-IN'|'te-IN'|'tr-TR'|'zh-CN'|'zh-TW'|'th-TH'|'en-ZA'|'en-NZ'|'vi-VN'|'sv-SE',
                            'DurationInSeconds': ...
                        },
                    ],
                    'Tags': [
                        {
                            'Key': 'string',
                            'Value': 'string'
                        },
                    ],
                    'Subtitles': {
                        'Formats': [
                            'vtt'|'srt',
                        ],
                        'SubtitleFileUris': [
                            'string',
                        ],
                        'OutputStartIndex': 123
                    },
                    'LanguageIdSettings': {
                        'string': {
                            'VocabularyName': 'string',
                            'VocabularyFilterName': 'string',
                            'LanguageModelName': 'string'
                        }
                    },
                    'ToxicityDetection': [
                        {
                            'ToxicityCategories': [
                                'ALL',
                            ]
                        },
                    ]
                }
            }
            """

            # 스크립트 uri
            script_uri = response["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
            # 스크립트 json 파일
            script_response = requests.get(script_uri)
            # 스크립트 내용
            script_data = json.loads(script_response.text)
            """ script syntex
            {
                "jobName": "7035cb7c-b215-4207-a2de-8a2b08a4fb9b",
                "accountId": "426848565412",
                "results": {
                    "transcripts": [{"transcript": "보시면 다음과 ... 있고요. "}],
                    "items": [
                        {
                            "start_time": "0.12",
                            "end_time": "0.48",
                            "alternatives": [{"confidence": "0.6093", "content": "보시면"}],
                            "type": "pronunciation",
                        },
                        {
                            "start_time": "0.48",
                            "end_time": "0.89",
                            "alternatives": [{"confidence": "1.0", "content": "다음과"}],
                            "type": "pronunciation",
                        },
                        {
                            "start_time": "5.4",
                            "end_time": "5.84",
                            "alternatives": [{"confidence": "0.9999", "content": "있고요"}],
                            "type": "pronunciation",
                        },
                        {
                            "alternatives": [{"confidence": "0.0", "content": "."}],
                            "type": "punctuation",
                        },
                    ],
                },
                "status": "COMPLETED",
            }
            """
            script_text = script_data["results"]["transcripts"]
            script_items = script_data["results"]["items"]
            return script_text, script_items

        def get_gpt_script(script_text: str) -> str:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello!"},
                ],
            )
            pass

        """
        
        
        
        1. 오디오 파일 어플리케이션 컨테이너에 전송
            - 앱 컨테이너 (aws transcript, chatGPT)
        2. 데이터 전송
            - 이 때 원본과 gpt스크립트, gpt 토큰 저장
            - 단어별 타임스크립트는 저장x 전송만
        3. 데이터 전송
        """

    def put(self, request, pk):
        """
        1. 수정된 원본 스크립트 받기
        2. GPT에게 답 받기
        3. 수정된 사항 저장, 토큰 저장
        """
