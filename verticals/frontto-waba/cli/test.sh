#!/bin/bash

curl -i -X POST \
  "https://graph.facebook.com/v22.0/598259000035700/messages" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "528128633029",
    "type": "text",
    "text": {
        "body":"Hello world..."
    }
  }'