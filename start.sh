#!/bin/bash

# Check the operating system
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  python3 yys.py
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
  # Linux
  python3 yys.py
elif [[ "$OSTYPE" == "msys"* ]]; then
  # Windows (using Git Bash or similar)
  python yys.py
else
  echo "Unsupported operating system."
fi
