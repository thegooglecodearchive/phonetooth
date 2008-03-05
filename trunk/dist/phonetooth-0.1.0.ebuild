# Copyright 1999-2008 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

inherit autotools eutils

DESCRIPTION="Lightweight video thumbnailer that can be used by file managers"
HOMEPAGE="http://code.google.com/p/phonetooth"
SRC_URI="http://${PN}.googlecode.com/files/${P}.tar.gz"

LICENSE="GPL-2"
SLOT="0"
KEYWORDS="alpha amd64 arm hppa ia64 ppc ppc64 sparc x86"
IUSE=""

RDEPEND="dev-python/pygtk
	 dev-python/pybluez
	 app-mobilephone/obexftp"
DEPEND="${RDEPEND}"

pkg_setup() {
	if ! built_with_use app-mobilephone/obexftp python ; then
		eerror "app-mobilephone/obexftp has to be compiled with USE=python"
		die "Needed USE-flag for obexftp not found."
	fi
}

src_compile() {
	econf
	emake || die "emake failed."
}

src_install() {
	emake DESTDIR="${D}" install || die "emake install failed."
	dodoc AUTHORS ChangeLog README TODO
}
