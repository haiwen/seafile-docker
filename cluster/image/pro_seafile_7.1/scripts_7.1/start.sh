#!/bin/bash

function start-front-end() {
    python /scripts/start.py
}

function start-back-end() {
    python /scripts/start.py --mode backend
}

case $1 in 
    "front-end" )
        start-front-end
        ;;
    "back-end" )
        start-back-end
        ;;
esac
