#!/bin/sh
docker build . --tag wsu-lookup
docker run -it wsu-lookup $*
