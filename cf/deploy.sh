#!/bin/sh

gcloud functions deploy fetch_events \
  --runtime python37 --trigger-http --allow-unauthenticated

#gcloud functions deploy speak \
#  --runtime python37 --trigger-http --allow-unauthenticated
