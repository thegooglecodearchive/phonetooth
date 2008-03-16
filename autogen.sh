#!/bin/sh -x
gettextize -f --no-changelog
aclocal -I m4
autoconf
automake --add-missing

