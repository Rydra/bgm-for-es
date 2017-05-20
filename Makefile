.ONESHELL:
debian-package:
	python setup.py --command-packages=stdeb.command bdist_deb
	cd deb_dist/es-bgm-*
	echo "systemctl daemon-reload" >> debian/postinst
	echo "systemctl enable bgm.service" >> debian/postinst
	dpkg-buildpackage -rfakeroot -uc -us
