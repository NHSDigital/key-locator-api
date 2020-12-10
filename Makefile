SHELL=/bin/bash -euo pipefail -O globstar

.PHONY: install build test publish release clean

install: install-python

install-python:
	poetry install

build: build-proxies

build-proxies:
	mkdir -p dist/proxies/live
	cp -Rv proxies/live/apiproxy dist/proxies/live

test:
	echo Test

publish:
	echo Publish

release:
	mkdir -p dist

clean:
	rm -rf dist

check-licenses:
	echo Check Licences