# Cloud Function

import datetime
import sys

import flask
from googleapiclient.discovery import build

CALENDAR = "c_0o20o0ld5alqctcj6f2981kh34@group.calendar.google.com"


def fetch_events(request: flask.Request) -> str:
    print("MDW: fetch_events() called")
    print(f"MDW: request is: {request}")
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and "maxResults" in request_json:
        maxResults = int(request_json["maxResults"])
    else:
        maxResults = 10

    print(f"MDW: maxResults is: {maxResults}")

    service = build("calendar", "v3")

    now = datetime.datetime.utcnow().isoformat() + "Z"
    events_result = (
        service.events()
        .list(
            calendarId=CALENDAR,
            timeMin=now,
            maxResults=maxResults,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])
    print(f"MDW: Got events: {events}")

    if not events:
        return {"result": []}
    return {"result": events}

#    for event in events:
#        start = event["start"].get("dateTime", event["start"].get("date"))
#        print(start, event["summary"])

