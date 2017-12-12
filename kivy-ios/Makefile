VERSION := $(shell grep 'version = ' buildozer.spec | sed 's/.*= *\([0-9\.]*\)/\1/')

build:
	buildozer -v ios debug

init:
	buildozer -v ios debug
	garden install --app mapview
	buildozer -v ios debug

load:
	buildozer -v ios deploy run logcat

git:
	LANG=C git commit -a
	git tag v${VERSION}
	git push
	git push origin v${VERSION}

