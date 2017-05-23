.ONESHELL:
debian-package:
	python setup.py --command-packages=stdeb.command sdist_dsc
	cd deb_dist/es-bgm-*

	cp ../../DEBIAN/conffiles debian/
	cp ../../DEBIAN/postinst debian/
	cp ../../DEBIAN/postrm debian/

	dpkg-buildpackage -rfakeroot -b -uc -us

tests:
	python setup.py test
