#!/bin/sh

cd SlimFramework.docset/Contents/Resources/Documents

httrack http://docs.slimframework.com/ \
  --display=2 --timeout=60 --retries=99 --sockets=7 \
  --connection-per-second=5 --max-rate=250000 \
  --keep-alive --depth=2 --mirror --robots=0 \
  --user-agent '$(httrack --version); dash-slimframework ()' \
  "+docs.slimframework.com/bootstrap/css/*" "+docs.slimframework.com/styles/*"
