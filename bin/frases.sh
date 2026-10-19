#!/usr/bin/env bash
frases=("これはスペースキー" "ホレンソン ドゥー アモンガス")
echo "${frases[RANDOM % ${#frases[@]}]}"
