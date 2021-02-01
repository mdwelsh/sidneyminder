# Cloud Function

import datetime
import sys
from typing import Any, Dict

import arrow
import flask
from googleapiclient.discovery import build
from google.cloud import texttospeech
import humanize

CALENDAR = "c_0o20o0ld5alqctcj6f2981kh34@group.calendar.google.com"


def fetch_events(request: flask.Request) -> Dict[str, Any]:
    print("MDW: fetch_events() called, request: {request}")
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and "maxResults" in request_json:
        maxResults = int(request_json["maxResults"])
    else:
        maxResults = 10
    print(f"MDW: maxResults is: {maxResults}")

    service = build("calendar", "v3")

    now = datetime.datetime.utcnow()
    now_iso = now.isoformat() + "Z"

    # For human formatting
    anow = arrow.utcnow().to("US/Pacific")
    datestring = anow.strftime("%A, %B %-d")
    timestring = anow.strftime("%-I:%M %p")

    events_result = (
        service.events()
        .list(
            calendarId=CALENDAR,
            timeMin=now_iso,
            maxResults=maxResults,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    # Parse out timestamps since CircuitPython doesn't have datetime.
    for event in events:
        event["now"] = {
            "date": datestring,
            "time": timestring,
            "dateTime": now_iso,
            "timestamp": int(now.timestamp()),
        }
        st = event["start"]["dateTime"]
        et = event["end"]["dateTime"]
        try:
            stp = datetime.datetime.strptime(st, "%Y-%m-%dT%H:%M:%S%z")
            etp = datetime.datetime.strptime(et, "%Y-%m-%dT%H:%M:%S%z")
            event["start"]["timestamp"] = int(stp.timestamp())
            event["start"]["when"] = stp.strftime("%-I:%M %p")
            until = humanize.naturaldelta(arrow.get(stp) - anow)
            event["start"]["until"] = until
            event["end"]["timestamp"] = int(etp.timestamp())
        except Exception as e:
            warning = f"Warning: {e}"
            print(warning)
            event["start"]["warning"] = warning

    if not events:
        return {"result": []}
    return {"result": events}


def speak(request: flask.Request) -> str:
    print(f"MDW: speak() called, request: {request}")
    request_json = request.get_json(silent=True)

    text = "You are a derp."
    languageCode = "en-GB"
    voice = "en-GB-Wavenet-F"

    if request_json:
        if "text" in request_json:
            text = request_json["text"]
        if "languageCode" in request_json:
            languageCode = request_json["languageCode"]
        if "voice" in request_json:
            voice = request_json["voice"]
    else:
        text = "You are a derp."
    print(f"MDW: text is: {text}")
    print(f"MDW: languageCode is: {languageCode}")
    print(f"MDW: voice is: {voice}")

    client = texttospeech.TextToSpeechClient()

    input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=languageCode, name=voice
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )
    response = client.synthesize_speech(
        input=input, voice=voice, audio_config=audio_config
    )
    return (
        response.audio_content,
        200,
        {"Content-Type": "application/octet-stream"},
    )
