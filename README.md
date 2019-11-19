# archinstall_gui
Graphical Arch Linux installer.<br>
All **errors should be reported here**, and no where else.<br>
See trouble-shooting a bit further down.

> **Note**: If you're not familiar with the installation process, please have a look at the comprehensive [Installation Guide](https://wiki.archlinux.org/index.php/Installation_guide).

# Screenshot

![screenshot](screenshot.png)

# Pre-built Live ISO:

A pre-built ISO from the steps below, can be found [here](https://hvornum.se/archiso/)

# Troubleshooting

In case of installation errors, check the "Install log",<br>
And post the local copy of `/root/archinstall.log` here on github as an issue.

> *note*: The `archinstall.log` might be elsewhere if you're running this as a standalone application to install from a already existing Arch Linux installation.

# Build into a Arch ISO medium

Follow the basics steps for **releng** on [Archiso wiki](https://wiki.archlinux.org/index.php/Archiso). Then, before you build, do the following steps:

```
# cd ~/archiso_build_folder
# cat <<EOF >> ./packages.x86_64
python
python-systemd
python-psutil
git
xorg-server
xorg-xinit
xorg-twm
chromium
EOF
# cat <<EOF >> ./airootfs/root/customize_airootfs.sh
cd /root
git clone --recursive https://github.com/Torxed/archinstall_gui.git
cp archinstall_gui/INSTALL/archinstall_gui.service /etc/systemd/system/
cp archinstall_gui/INSTALL/xinitrc /etc/X11/xinit/
cp -r archinstall_gui /srv/
chmod +x /srv/archinstall_gui/webgui.py
systemctl daemon-reload
systemctl enable archinstall_gui.service
EOF
# mkdir -p ./airootfs/etc/skel
# echo '[[ -z $DISPLAY && $XDG_VTNR -eq 1 ]] && sh -c "startx"' >> ./airootfs/etc/skel/.zprofile
```

This will auto-run the backend webservice that does all the actual work.<br>
Then, on boot it will launch `X` with `chromium` in full-screen mode *(thanks to the `xinitrc` from the `INSTALL` folder of this repo)*.

Now, do `sudo ./build.sh -v` and a finished ISO should pop out under `./out`.