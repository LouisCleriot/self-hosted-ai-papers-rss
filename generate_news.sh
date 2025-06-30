#! /bin/bash

source venv/bin/activate

python main.py

year=$(date +%Y)
month=$(date +%m)
day=$(date +%d)

cd newsletters/$year-$month-$day

pandoc newsletter_$year-$month-$day.md -o $year-$month-$day.pdf \
    --pdf-engine=xelatex -V mainfont="CaskaydiaCove Nerd Font" \
    -V monofont="CaskaydiaCove Nerd Font" \
    --resource-path=.:../../ \
    -V header-includes:"\usepackage{graphicx}"

cp $year-$month-$day.pdf ../../TODAY_NEWSLETTER.pdf