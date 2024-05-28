#!/usr/bin/env sh

main() {
    pkill -f memcached
    cd src
    memcached --port=15391 --daemon --memory-limit=1024
    gunicorn -b 127.0.0.1:27123 -w "$(nproc --all)" main:app
}

main "$@"
