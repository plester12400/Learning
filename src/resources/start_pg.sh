#!/usr/bin/env bash
export PATH=$PATH:/usr/local/bin
docker run --name pg_options -e POSTGRES_PASSWORD=password -it --rm -v pgdata:/var/lib/postgresql/data -p5432:5432 -d postgres