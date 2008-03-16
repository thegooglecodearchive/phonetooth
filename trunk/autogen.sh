#!/bin/sh -x
aclocal -I m4
autoconf
automake --add-missing
gettextize -f --no-changelog
