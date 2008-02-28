bin_SCRIPTS = phonetooth

pkgpython_PYTHON =  pyphonetooth/contacts.py \
                    pyphonetooth/contactsdialog.py \
                    pyphonetooth/mainwindow.py \
                    pyphonetooth/mobilephone.py \
                    pyphonetooth/preferencesdialog.py \
                    pyphonetooth/constants.py \
                    pyphonetooth/__init__.py

uidir = $(datadir)/phonetooth
ui_DATA =   ui/phonetooth.glade \
            ui/phonetooth.svg \
            ui/phonetooth-small.svg

desktopdir = $(datadir)/applications
desktop_DATA = data/phonetooth.desktop

EXTRA_DIST =    $(bin_SCRIPTS) \
                $(ui_DATA) \
                $(desktop_DATA)
