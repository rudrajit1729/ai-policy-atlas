#!/bin/zsh
# Double-click to open the AI Policy Atlas website on this Mac (http://localhost:8792). Close this window to stop it.
cd "$(dirname "$0")/v2/site" || exit 1
(sleep 1; open "http://localhost:8792/") &
python3 -m http.server 8792
