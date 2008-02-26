bin_SCRIPTS = phonetooth

pkgpython_PYTHON =  contacts.py \
                    contactsdialog.py \
                    mainwindow.py \
                    mobilephone.py \
                    preferencesdialog.py \
                    constants.py \
                    __init__.py

uidir = $(datadir)/phonetooth
ui_DATA = phonetooth.glade

desktopdir = $(datadir)/applications
desktop_DATA = data/phonetooth.desktop

iconsdir = $(datadir)/pixmaps
icons_DATA = data/phonetooth.svg

EXTRA_DIST =    $(bin_SCRIPTS) \
                $(ui_DATA) \
                $(desktop_DATA) \
                $(icons_DATA)