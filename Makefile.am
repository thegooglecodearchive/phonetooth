bin_SCRIPTS = phonetoothui

pkgpython_PYTHON =  phonetooth/contacts.py \
                    phonetooth/contactsdialog.py \
                    phonetooth/selectcontactsdialog.py \
                    phonetooth/mergecontactsdialog.py \
                    phonetooth/mainwindow.py \
                    phonetooth/filetransfer.py \
                    phonetooth/mobilephone.py \
                    phonetooth/mobilephonegammu.py \
                    phonetooth/mobilephonefactory.py \
                    phonetooth/bluetoothdiscovery.py \
                    phonetooth/bluetoothconnection.py \
                    phonetooth/serialconnection.py \
                    phonetooth/preferences.py \
                    phonetooth/preferencesdialog.py \
                    phonetooth/constants.py \
                    phonetooth/sms.py \
                    phonetooth/sendmessagedialog.py \
                    phonetooth/bit7alphabet.py \
                    phonetooth/__init__.py

uidir = $(datadir)/phonetooth
ui_DATA =   ui/phonetooth.glade \
            ui/phonetooth.svg \
            ui/phonetooth-small.svg

desktopdir = $(datadir)/applications
desktop_DATA = data/phonetooth.desktop

EXTRA_DIST =    config.rpath\
                $(bin_SCRIPTS) \
                $(ui_DATA) \
                $(desktop_DATA)

SUBDIRS = po

ACLOCAL_AMFLAGS = -I m4
