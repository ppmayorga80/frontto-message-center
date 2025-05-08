#!/usr/bin/env bash

WA_ACCESS_TOKEN=EAATjU8hegLkBO3oTWGBhdrqf8TcjiV1GVyokmnbmeNIpm4kWO4ZA9o03IgQHJng1UiAQpHsIIqmUwzZAXGZAsZCy4bofUIfiDMhzyfBobZAJFsV71UZCFIZBCpzVu2zp3uGfzZAcmm23YbZC1Dwt27t98RB8HMNJYgFKnZA0hwJZCOMAIQ91LfToyir3Tv4XQhnkBLJmO6OSuYo3VyQMLqm9VBEWgU8EgwjilKQwZAiD8EzF9P4ZD
WA_PHONE_ID=598259000035700
WAB_ACCOUNT_ID=685424180481373


X_TO=$1
X_MSG=$2

X_TO="528128633029"


curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${WA_ACCESS_TOKEN}" \
  -d '{
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": "528128633029",
    "type": "text",
    "text": {
      "body": "Hello world with CURL"
    }
  }' \
  "https://graph.facebook.com/v22.0/${WA_PHONE_ID}/messages"

#curl -X POST "https://graph.facebook.com/v22.0/${WA_PHONE_ID}/messages" \
#  -H "Authorization: Bearer ${WA_ACCESS_TOKEN}" \
#  -H "Content-Type: application/json" \
#  -d '{
#    "messaging_product": "whatsapp",
#    "recipient_type": "individual",
#    "to": "'"${X_TO}"'",
#    "type": "text",
#    "text": { "body": "¡Hola! Este es un mensaje de prueba sin plantilla en WhatsApp Business API." }
#  }' -i

