.ONESHELL:
debian-package:
	python setup.py --command-packages=stdeb.command bdist_deb
	cd deb_dist/es-bgm-*
	echo "systemctl daemon-reload" >> debian/postinst
	echo "systemctl enable bgm" >> debian/postinst
	echo "systemctl start bgm" >> debian/postinst
	dpkg-buildpackage -rfakeroot -uc -us

tests:
	py.test
