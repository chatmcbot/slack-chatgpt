#!/bin/bash

# Check if the "name" parameter is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <name>"
  exit 1
fi

# Set the "name" parameter
name="$1"

# Run the specified command
source ".env.${name}"
npx serverless deploy
