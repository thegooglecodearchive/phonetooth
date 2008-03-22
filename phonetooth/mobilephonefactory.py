#    Copyright (C) 2008 Dirk Vanden Boer <dirk.vdb@gmail.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from phonetooth import mobilephone
from phonetooth import mobilephonegammu
from phonetooth import bluetoothconnection
from phonetooth import serialconnection

from gettext import gettext as _

def createPhone(prefs):
    if prefs.connectionMethod == 'gammu':
        return mobilephonegammu.MobilePhoneGammu(prefs.gammuIndex)
    elif prefs.connectionMethod == 'bluetooth':
        if prefs.btDevice == None:
            raise Exception, _('No device configured in the preferences')
        return mobilephone.MobilePhone(bluetoothconnection.BluetoothConnection(prefs.btDevice.address, prefs.btDevice.port))
    elif prefs.connectionMethod == 'customPort':
        return mobilephone.MobilePhone(serialconnection.SerialConnection(prefs.customPort))
    else:
        raise Exception, 'Invalid back end specified: ' + backEnd

