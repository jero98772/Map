#!/bin/sh
# Convert every manim video in core/static/video/ (and its dark/ and light/ theme
# folders) to a looping GIF at the same place under core/static/gif/.
#   cd src && sh scripts/videos_to_gif.sh
# Two-pass ffmpeg: build a palette per video, then dither with it (much sharper than the default).
set -e
FPS=${FPS:-12}
WIDTH=${WIDTH:-720}
cd "$(dirname "$0")/.."
for dir in "" dark/ light/; do
    mkdir -p "core/static/gif/$dir"
    for mp4 in core/static/video/$dir*.mp4; do
        [ -e "$mp4" ] || continue
        name=$(basename "$mp4" .mp4)
        # the full deck and the teaser are played as video, not as GIF
        case $name in InterpreterTutorial|PythonExecutionJourney) continue ;; esac
        palette=$(mktemp --suffix=.png)
        filters="fps=$FPS,scale=$WIDTH:-1:flags=lanczos"
        ffmpeg -loglevel error -y -i "$mp4" -vf "$filters,palettegen=stats_mode=diff" "$palette"
        ffmpeg -loglevel error -y -i "$mp4" -i "$palette" \
            -lavfi "$filters [x]; [x][1:v] paletteuse=dither=bayer:bayer_scale=5" \
            -loop 0 "core/static/gif/$dir$name.gif"
        rm -f "$palette"
        echo "core/static/gif/$dir$name.gif"
    done
done
