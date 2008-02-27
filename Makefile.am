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
            ui/phonetooth.svg \
            ui/phonetooth-small.svg

desktopdir = $(datadir)/applications
desktop_DATA = data/phonetooth.desktop

EXTRA_DIST =    $(bin_SCRIPTS) \
                $(ui_DATA) \
                $(desktop_DATA)
