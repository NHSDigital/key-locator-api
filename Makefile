SHELL=/bin/bash -euo pipefail -O globstar

.PHONY: install test publish release clean

install: install-python
	npm --prefix=specification install

install-python:
	poetry install

test:
	npm --prefix=specification run test

publish:
	echo Publish

release: ensure-dist-exists build-proxies build-spec

ensure-dist-exists:
	mkdir -p dist

build-proxies:
	mkdir -p dist/proxies/live
	cp -Rv proxies/live/apiproxy dist/proxies/live

build-spec:
	npm --prefix=specification run build-spec
	cp specification/dist/key-locator-api.json dist

clean:
	rm -rf dist
	rm -rf specification/dist

check-licenses:
	npm --prefix=specification run check-licenses

lint:
	npm --prefix=specification run lint