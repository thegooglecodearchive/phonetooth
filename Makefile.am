bin_SCRIPTS = phonetoothui

pkgpython_PYTHON =  phonetooth/bit7alphabet.py \
                    phonetooth/bluetoothdiscovery.py \
                    phonetooth/bluetoothconnection.py \
                    phonetooth/constants.py \
                    phonetooth/contacts.py \
                    phonetooth/contactsdialog.py \
                    phonetooth/filecollection.py \
                    phonetooth/filetransfer.py \
                    phonetooth/filetransferdialog.py \
                    phonetooth/mainwindow.py \
                    phonetooth/mergecontactsdialog.py \
                    phonetooth/mobilephone.py \
                    phonetooth/mobilephonegammu.py \
                    phonetooth/mobilephonefactory.py \
                    phonetooth/messageinput.py \
                    phonetooth/phonebrowser.py \
                    phonetooth/phonebrowserhandler.py \
                    phonetooth/preferences.py \
                    phonetooth/preferencesdialog.py \
                    phonetooth/selectcontactsdialog.py \
                    phonetooth/sendmessagedialog.py \
                    phonetooth/serialconnection.py \
                    phonetooth/sms.py \
                    phonetooth/transferinfo.py\
                    phonetooth/transfermanager.py\
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
