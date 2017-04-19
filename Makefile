VERSION := $(shell grep 'version = ' buildozer.spec | sed 's/.*= *\([0-9\.]*\)/\1/')

build:
	buildozer -v android debug

load:
	buildozer -v android deploy run logcat

git:
	LANG=C git commit -a
	git tag v${VERSION}
	git push
	git push origin v${VERSION}

