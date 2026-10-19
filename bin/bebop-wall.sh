#!/usr/bin/env bash
# Fondo animado: salta entre clips con mpvpaper
DIR="$HOME/Downloads"
SOCK=/tmp/mpv-socket
# formato: episodio:segundo_inicio:duracion
PLAYLIST=("1:160:16" "2:131:25" "3:1116:10" "1:1337:19")
# sid=2 = "Full Subs" (ingles completo); sub-ass=yes usa el estilo original del .mkv
OPTS="osd-level=0 sub-use-margins=yes sub-ass-force-margins=yes no-audio sid=2 sub-ass=yes sub-ass-override=scale sub-scale=0.6 osd-on-seek=no video-margin-ratio-top=0.15 video-margin-ratio-bottom=0.15 input-ipc-server=$SOCK"

pkill mpvpaper
rm -f "$SOCK"
mpvpaper -o "$OPTS" '*' "$DIR/Ep01.mkv" > /tmp/mpvpaper.log 2>&1 < /dev/null &

for i in $(seq 50); do [ -S "$SOCK" ] && break; sleep 0.1; done

while true; do
  for item in "${PLAYLIST[@]}"; do
    IFS=: read -r ep start dur <<< "$item"
    printf 'loadfile "%s/Ep0%s.mkv"\n' "$DIR" "$ep" | socat - "$SOCK" > /dev/null
    sleep 0.3
    # mpv vuelve a la pista 1 (solo carteles) en cada archivo nuevo: se re-elige la completa
    printf 'set sid 2\n' | socat - "$SOCK" > /dev/null
    printf 'seek %s absolute\n' "$start" | socat - "$SOCK" > /dev/null
    sleep "$dur"
  done
done
