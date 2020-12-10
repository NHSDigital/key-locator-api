SHELL=/bin/bash -euo pipefail -O globstar

.PHONY: install build test publish release clean

install:
	echo Install

build: build-proxies

test:
	echo Test

publish:
	echo Publish

release:
	mkdir -p dist

clean:
	rm -rf dist

build-proxies:
	mkdir -p dist/proxies/live
	cp -Rv proxies/live/apiproxy dist/proxies/live
