#!/bin/sh

# Decrypt the file
mkdir $HOME/secrets
# --batch to prevent interactive command
# --yes to assume "yes" for questions
gpg --quiet --batch --yes --decrypt --passphrase="$SERVICE_DECRYPT_PASS" \
--output $HOME/secrets/service_token.json service_token.json.gpg