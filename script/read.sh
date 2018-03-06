#!/bin/bash

#https://stackoverflow.com/questions/9893175/google-text-to-speech-api

text=$1
uuid=`date +%Y%m%d%H%M%S`
down_mp3="curl 'https://translate.google.com/translate_tts?ie=UTF-8&q=$text&tl=zh-CN&client=tw-ob' -H 'Referer: http://translate.google.com/' -H 'User-Agent: stagefright/1.2 (Linux;Android 5.0)' -o /tmp/$uuid.wav"
echo $down_mp3
eval $down_mp3
cvlc --play-and-exit /tmp/$uuid.wav

