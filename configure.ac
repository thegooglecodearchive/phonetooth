AC_INIT([phonetooth],[0.4.1])
AC_CONFIG_SRCDIR([phonetooth])
AM_INIT_AUTOMAKE

AM_PATH_PYTHON
AM_PO_SUBDIRS

if ! $PYTHON -c 'import gtk' > /dev/null 2>&1; then 
  AC_MSG_ERROR([Python module 'gtk' not found, install pygtk package])
fi

AC_CONFIG_FILES([phonetooth/constants.py:phonetooth/constants.py.in po/Makefile.in])
AC_CONFIG_FILES([data/phonetooth.desktop:data/phonetooth.desktop.in])

AC_CONFIG_FILES(Makefile)
AC_OUTPUT

