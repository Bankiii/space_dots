#!/usr/bin/env bash
# Fondo animado: salta entre clips con mpvpaper
DIR="$HOME/Downloads"
SOCK=/tmp/mpv-socket
# formato: episodio:segundo_inicio:duracion
PLAYLIST=("1:160:16" "2:131:25" "3:1116:10" "1:1337:19")
OPTS="no-audio sid=2 sub-ass=no sub-font-size=20 sub-color=#FDDA0D sub-bold=yes sub-border-size=1 sub-shadow-color=#000000 sub-shadow-offset=2 sub-margin-y=40 video-margin-ratio-top=0.15 video-margin-ratio-bottom=0.15 osd-on-seek=no input-ipc-server=$SOCK"

pkill mpvpaper
rm -f "$SOCK"
mpvpaper -o "$OPTS" '*' "$DIR/Ep01.mkv" > /tmp/mpvpaper.log 2>&1 < /dev/null &

for i in $(seq 50); do [ -S "$SOCK" ] && break; sleep 0.1; done

while true; do
  for item in "${PLAYLIST[@]}"; do
    IFS=: read -r ep start dur <<< "$item"
    printf 'loadfile "%s/Ep0%s.mkv"\n' "$DIR" "$ep" | socat - "$SOCK" > /dev/null
    sleep 0.3
    printf 'seek %s absolute\n' "$start" | socat - "$SOCK" > /dev/null
    sleep "$dur"
  done
done
