#!/bin/sh
# get some vars from env and write to json
if [ -z "$FORCE_HTTP" ]; then
  API_ROOT="http://api.$VIRTUAL_HOST_ROOT/"
else
  API_ROOT="https://api.$VIRTUAL_HOST_ROOT/"
fi
RUNTIME_CONF="{
  \"API_ROOT\": \"$API_ROOT\"
}"
echo $RUNTIME_CONF > ./src/conf.json
