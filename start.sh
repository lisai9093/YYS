#!/bin/bash
# Check the operating system
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  python3 main.py $@ &
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
  # Linux
  python3 main.py $@ &
elif [[ "$OSTYPE" == "msys"* ]]; then
  # Windows (using Git Bash or similar)
  python main.py $@ &
else
  echo "Unsupported operating system."
fi
