from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import exceptions

from . import serializers
from .models import Audio
from users.models import User

import environ
import os
from django.conf import settings

import boto3
import time
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


# 내일 django 정적 파일 저장소 설정부터 시작하기
class UploadAudio(APIView):
    permission_classes = [IsAuthenticated]

    def get_gpt_script(self, script_text: str) -> list:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Your role only organizes the input. And only answer in Korean",
                },
                {"role": "user", "content": script_text},
            ],
        )
        """ cimpletion syntax
        {
        "id": "chatcmpl-7hWY4zomRdwCgFdt53y7F6Wt6FjnS",
        "object": "chat.completion",
        "created": 1690607576,
        "model": "gpt-3.5-turbo-0613",
        "choices": [
            {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Hello! How can I assist you today?"
            },
            "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 19,
            "completion_tokens": 9,
            "total_tokens": 28
        }
        }
        """

        return (
            completion["choices"][0]["message"]["content"],
            completion["usage"]["completion_tokens"],
        )

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
        def wait_for_transcription(job_name: str):
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
            script_text = script_data["results"]["transcripts"][0]["transcript"]
            script_items = script_data["results"]["items"]
            return (script_text, script_items)

        # user = User.objects.get(username=request.user)
        try:
            user = User.objects.get(username=request.user)
            file = request.data.get("file")
            title = request.data["title"]

            test_data = {
                "origin_script": "결과 또한 빠르게 나오게 됩니다. 최종적으로 세이브것들을 통해서 저희가 이미지를 조정할 수 있게 됩니다.",
                "modified_script": "이미지 조정을 위해 세이브한 결과는 빠르게 나오게 됩니다. 세이브한 것들을 통해 우리는 이미지를 최종적으로 조정할 수 있습니다.",
                "charecters": [
                    {
                        "start_time": "0.0",
                        "end_time": "0.37",
                        "alternatives": [{"confidence": "0.5994", "content": "결과"}],
                        "type": "pronunciation",
                    },
                    {
                        "start_time": "0.37",
                        "end_time": "0.68",
                        "alternatives": [{"confidence": "1.0", "content": "또한"}],
                        "type": "pronunciation",
                    },
                    {
                        "start_time": "0.85",
                        "end_time": "1.19",
                        "alternatives": [{"confidence": "1.0", "content": "빠르게"}],
                        "type": "pronunciation",
                    },
                    {
                        "start_time": "1.19",
                        "end_time": "1.41",
                        "alternatives": [{"confidence": "0.9979", "content": "나오게"}],
                        "type": "pronunciation",
                    },
                    {
                        "start_time": "1.41",
                        "end_time": "1.71",
                        "alternatives": [{"confidence": "0.9814", "content": "됩니다"}],
                        "type": "pronunciation",
                    },
                    {
                        "alternatives": [{"confidence": "0.0", "content": "."}],
                        "type": "punctuation",
                    },
                    {
                        "start_time": "3.42",
                        "end_time": "4.03",
                        "alternatives": [{"confidence": "0.9999", "content": "최종적으로"}],
                        "type": "pronunciation",
                    },
                    {
                        "start_time": "6.35",
                        "end_time": "6.53",
                        "alternatives": [{"confidence": "0.9935", "content": "있게"}],
                        "type": "pronunciation",
                    },
                    {
                        "start_time": "6.53",
                        "end_time": "6.9",
                        "alternatives": [{"confidence": "0.9996", "content": "됩니다"}],
                        "type": "pronunciation",
                    },
                    {
                        "alternatives": [{"confidence": "0.0", "content": "."}],
                        "type": "punctuation",
                    },
                ],
            }
            return Response(test_data, status=status.HTTP_200_OK)
        except:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        # 프론트엔드 연결 테스트

        serializer = serializers.AudioFirstSaveSerializer(
            data={
                "user": user.pk,
                "file": file,
                "title": title,
            },
        )

        if serializer.is_valid():
            audio = serializer.save()
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        job_name = audio.file.name
        print("wait 3 second...")
        time.sleep(3)

        origin_script, charecters = wait_for_transcription(job_name=job_name)
        modified_script, using_token = self.get_gpt_script(script_text=origin_script)

        # 사용한 토큰 저장
        user.using_gpt_token += using_token
        user.save()

        audio.origin_script = origin_script
        audio.modified_script = modified_script

        serializer = serializers.AudioSerializer(
            audio,
            data={"origin_script": origin_script, "modified_script": modified_script},
            partial=True,
        )

        if serializer.is_valid():
            new_audio = serializer.save()

            """Response data syntex
            {
                "origin_script": "결과 또한 빠르게 나오게 됩니다. 최종적으로 세이브것들을 통해서 저희가 이미지를 조정할 수 있게 됩니다.",
                "modified_script": "이미지 조정을 위해 세이브한 결과는 빠르게 나오게 됩니다. 세이브한 것들을 통해 우리는 이미지를 최종적으로 조정할 수 있습니다.",
                "charecters": [
                    {
                        "start_time": "0.0",
                        "end_time": "0.37",
                        "alternatives": [
                            {
                                "confidence": "0.5994",
                                "content": "결과"
                            }
                        ],
                        "type": "pronunciation"
                    },
                    {
                        "start_time": "0.37",
                        "end_time": "0.68",
                        "alternatives": [
                            {
                                "confidence": "1.0",
                                "content": "또한"
                            }
                        ],
                        "type": "pronunciation"
                    },
                    {
                        "start_time": "0.85",
                        "end_time": "1.19",
                        "alternatives": [
                            {
                                "confidence": "1.0",
                                "content": "빠르게"
                            }
                        ],
                        "type": "pronunciation"
                    },
                    {
                        "start_time": "1.19",
                        "end_time": "1.41",
                        "alternatives": [
                            {
                                "confidence": "0.9979",
                                "content": "나오게"
                            }
                        ],
                        "type": "pronunciation"
                    },
                    {
                        "start_time": "1.41",
                        "end_time": "1.71",
                        "alternatives": [
                            {
                                "confidence": "0.9814",
                                "content": "됩니다"
                            }
                        ],
                        "type": "pronunciation"
                    },
                    {
                        "alternatives": [
                            {
                                "confidence": "0.0",
                                "content": "."
                            }
                        ],
                        "type": "punctuation"
                    },
                    {
                        "start_time": "3.42",
                        "end_time": "4.03",
                        "alternatives": [
                            {
                                "confidence": "0.9999",
                                "content": "최종적으로"
                            }
                        ],
                        "type": "pronunciation"
                    },
                    .
                    .
                    .
                    {
                        "start_time": "6.35",
                        "end_time": "6.53",
                        "alternatives": [
                            {
                                "confidence": "0.9935",
                                "content": "있게"
                            }
                        ],
                        "type": "pronunciation"
                    },
                    {
                        "start_time": "6.53",
                        "end_time": "6.9",
                        "alternatives": [
                            {
                                "confidence": "0.9996",
                                "content": "됩니다"
                            }
                        ],
                        "type": "pronunciation"
                    },
                    {
                        "alternatives": [
                            {
                                "confidence": "0.0",
                                "content": "."
                            }
                        ],
                        "type": "punctuation"
                    }
                ]
            }
            """
            return Response(
                {
                    "result": {
                        "origin_script": origin_script,
                        "modified_script": modified_script,
                        "charecters": charecters,
                        "audio_pk": new_audio.pk,
                        "audio_pk": "s3_audio_src",
                    }
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_417_EXPECTATION_FAILED,
            )

    def put(self, request):
        print(request.data)
        modified_charecters = request.data["charecters"]
        modified_charecters = json.loads(modified_charecters)
        print(modified_charecters)
        new_origin_script = ""
        # 수정된 원본 스크립트 생성
        print("단어 조합 시작")
        print(modified_charecters[0])
        for charecter in modified_charecters:
            """charecters syntex
            {
                "start_time": "0.0",
                "end_time": "0.37",
                "alternatives": [
                    {
                        "confidence": [0,1] float,
                        "content": string
                        }
                    ],
                "type": "pronunciation" | "punctuation"
            }
            """
            if charecter["type"] == "pronunciation":
                new_origin_script += " "
            new_origin_script += charecter["alternatives"][0]["content"]
        print("단어 조합 끝")
        return Response({"finalScript": new_origin_script}, status=status.HTTP_200_OK)

        new_modified_script, using_token = self.get_gpt_script(new_origin_script)

        # 사용한 토큰 저장
        # user = User.objects.get(username=request.user)
        user = User.objects.get(username="admin")
        user.using_gpt_token += using_token
        user.save()

        serializer = serializers.AudioSerializer(
            # Audio.objects.get(user=request.user),
            Audio.objects.get(pk=request.data["pk"]),
            data={
                "origin_script": new_origin_script,
                "modified_script": new_modified_script,
            },
            partial=True,
        )
        print(f"new_origin_script:{new_origin_script}")
        print(f"new_modified_script:{new_modified_script}")
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "origin_script": new_origin_script,
                    "modified_script": new_modified_script,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
