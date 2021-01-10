#!/bin/sh

gcloud functions deploy fetch_events \
  --runtime python37 --trigger-http --allow-unauthenticated
