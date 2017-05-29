all:	build modules

build:
	make -C kivy build

load:
	make -C kivy load

modules:
	make -C modules

git:
	LANG=C git commit -a
	git tag v${VERSION}
	git push
	git push origin v${VERSION}

