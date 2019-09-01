#!/bin/sh

rm -rf Slim_Framework.docset/Contents/Resources

httrack https://www.slimframework.com/docs/v4 \
  -O Slim_Framework.docset/Contents/Resources/Documents,cache -I0 \
  --display=2 --timeout=60 --retries=99 --sockets=7 \
  --connection-per-second=5 --max-rate=250000 \
  --keep-alive --depth=5 --mirror --clean --robots=0 \
  --user-agent '$(httrack --version); dash-slimframework ()' \
  "-www.slimframework.com/docs/v2" "-www.slimframework.com/docs/v3" \
  "+www.slimframework.com/assets/*" "+maxcdn.bootstrapcdn.com/font-awesome/*"
