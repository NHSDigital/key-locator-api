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

release: build-proxies build-spec build-smoke-tests

build-proxies:
	mkdir -p dist/proxies/live
	cp -Rv proxies/live/apiproxy dist/proxies/live

build-spec:
	npm --prefix=specification run build-spec
	cp specification/dist/key-locator-api.json dist

build-smoke-tests:
	cp -Rv tests dist

clean:
	rm -rf dist
	rm -rf specification/dist

check-licenses:
	npm --prefix=specification run check-licenses

lint:
	npm --prefix=specification run lint
