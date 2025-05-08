#!/usr/bin/env bash

# Default METHOD to GET if not provided
METHOD="${1:-POST}"

if [[ "$METHOD" == "GET" ]]; then
  # Retrieve the secret token from Secret Manager
  TOKEN="$(gcloud secrets versions access latest --secret="wa-verify-token")" || {
    echo "Failed to retrieve secret."
    exit 1
  }
  TOKEN="${TOKEN}"
  # Generate a challenge with a random integer
  CHALLENGE="$RANDOM"

  # Use curl to send the GET request
  RESPONSE="$(curl -s "http://127.0.0.1:8080?hub.verify_token=${TOKEN}&hub.mode=subscribe&hub.challenge=${CHALLENGE}")"

  # Output the response
  echo "Response  >>$RESPONSE<<"
  echo "Challenge >>$CHALLENGE<<"
fi

if [[ "$METHOD" == "POST" ]]; then
  curl -X POST \
     -H "Content-Type: application/json" \
     -d '{
           "entry": [
             {
               "changes": [
                 {
                   "value": {
                     "messages": [
                       {
                         "from": "1234567890",
                         "text": {
                           "body": "Hello from curl!"
                         }
                       }
                     ]
                   }
                 }
               ]
             }
           ]
         }' \
     http://127.0.0.1:8080

fi
