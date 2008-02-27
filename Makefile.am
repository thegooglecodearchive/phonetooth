bin_SCRIPTS = phonetooth/phonetooth

pkgpython_PYTHON =  phonetooth/contacts.py \
                    phonetooth/contactsdialog.py \
                    phonetooth/mainwindow.py \
                    phonetooth/mobilephone.py \
                    phonetooth/preferencesdialog.py \
                    phonetooth/constants.py \
                    phonetooth/__init__.py

uidir = $(datadir)/phonetooth
ui_DATA =   ui/phonetooth.glade \
            data/phonetooth-small.svg

desktopdir = $(datadir)/applications
desktop_DATA = data/phonetooth.desktop

iconsdir = $(datadir)/pixmaps
icons_DATA = data/phonetooth.svg

EXTRA_DIST =    $(bin_SCRIPTS) \
                $(ui_DATA) \
                $(desktop_DATA) \
                $(icons_DATA)