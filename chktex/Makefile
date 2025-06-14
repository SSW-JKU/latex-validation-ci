#
#  Makefile for ChkTeX project, creates the stuff.
#  Copyright (C) 1996 Jens T. Berger Thielemann
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#  Contact the author at:
#		Jens Berger
#		Spektrumvn. 4
#		N-0666 Oslo
#		Norway
#		E-mail: <jensthi@ifi.uio.no>
#


prefix=/mnt/c/Users/katha/Documents/Studium/Master/SEMESTER_3/Project_in_Software_Engineering/playground/tools
exec_prefix=${prefix}
bindir=${exec_prefix}/bin
datarootdir=${prefix}/share
datadir=${datarootdir}
sysconfdir=${prefix}/etc
srcdir=.
mandir=${datarootdir}/man
INSTALL=/usr/bin/install -c
INSTALL_PROGRAM=${INSTALL}
INSTALL_DATA=${INSTALL} -m 644
MKDIR_P=/usr/bin/mkdir -p
CLEAN=

CC=gcc
CFLAGS=-g -O2 -Wstrict-prototypes -Wall
CPPFLAGS= -I$(srcdir) -I. $(DEFS) $(USRDEFS)
DEFS=-DHAVE_CONFIG_H
LIBS=
LDFLAGS=
LN_S=ln -s
LATEX=/usr/bin/latex
PDFLATEX=/usr/bin/pdflatex
DVIPS=/usr/bin/dvips
PS2PDF=ps2pdf
PERL5=/usr/bin/perl
LATEX2HTML=
LYNX=
GROFF=groff -man -P-bu -Tlatin1
SHELL=/bin/sh

BUILT_SCRIPTS= deweb
SCRIPTS= chkweb

USRDEFS=-DSYSCONFDIR=\"$(sysconfdir)\" -D__unix__



#####################################################################

EXTRA_DIST=configure.ac Makefile.in stamp-h.in config.h.in rmeheader.in \
	MakeHTML.pl ChkTeX.tex.in aclocal.m4 NEWS \
	chkweb deweb.in COPYING chktex.1 chkweb.1 deweb.1 \
	input.tex Test.tex Test.pcre.out Test.posix-ere.out Test.nore.out configure \
	install-sh lacheck chktexrc \
	$(wildcard m4/*.m4)

# created by configure
CONFIG_DIST=ChkTeX.tex ChkTeXRC.tex chktexrc

# created at make time
BUILT_DIST=chktex.doc chkweb.doc deweb.doc README ChkTeX.dvi

CSOURCES=ChkTeX.c FindErrs.c OpSys.c Resource.c Utility.c

# The sources are the C sources and possibly the files with the same base name
# but ending with .h
SOURCEFILES=$(CSOURCES) $(wildcard $(CSOURCES:.c=.h)) types.h

DISTFILES=$(EXTRA_DIST) $(SOURCEFILES)

all: chktex chktexrc

DISTDIR:=chktex-1.7.9
dist: $(DISTDIR).tar.gz
$(DISTDIR).tar.gz: $(DISTFILES) $(CONFIG_DIST) $(BUILT_DIST) html
	rm -r $(DISTDIR) 2>/dev/null ; true
	$(MKDIR_P) $(DISTDIR)
	for f in $(DISTFILES) ; do \
	  cp $(srcdir)/$$f $(DISTDIR) ; \
	done
	cp $(CONFIG_DIST) $(BUILT_DIST) $(DISTDIR)
	$(MKDIR_P) $(DISTDIR)/html
	cp HTML/ChkTeX/*.{html,css} $(DISTDIR)/html
	rm -f $(DISTDIR).tar.gz
	tar --owner=0 --group=0 -chzf $@ $(DISTDIR)
	rm -rf $(DISTDIR)

########################################################################

.c.o:
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@
CLEAN+=$(CSOURCES:.c=.o)

.%.d: %.c
	$(CC) -M $(CPPFLAGS) $< > $@.tmp
	sed 's,\($*\)\.o *:,\1.o $@ : Makefile,g' $@.tmp > $@
	-rm -f $@.tmp 2>/dev/null

DEPFILES=$(patsubst %.c,.%.d,$(CSOURCES))
CLEAN+=$(DEPFILES)

ifeq ($(findstring clean,$(MAKECMDGOALS)),)
include $(DEPFILES)
endif

###################### MAIN DEPENDENCIES ################################

OBJS= ChkTeX.o FindErrs.o OpSys.o Resource.o Utility.o

MAKETEST= (builddir=`pwd` ; cd $(srcdir) ; $${builddir}/chktex -mall -r -g0 -lchktexrc -v5 -q Test.tex || :)

# We can't grep the output of chtex because it might not be built yet
TestOutFile := $(shell sed -n 's/.*HAVE_\(.*RE\) 1.*/\1/p' config.h | tr "A-Z_" "a-z-")
ifeq ($(TestOutFile),)
TestOutFile := Test.nore.out
else
TestOutFile := Test.$(TestOutFile).out
endif
$(srcdir)/$(TestOutFile): $(srcdir)/Test.tex $(srcdir)/input/file
	-rm -f $(srcdir)/$(TestOutFile)
	@echo ""
	@echo "***Warning: creating $(TestOutFile)***"
	@echo ""
	$(MAKETEST) 1> $(srcdir)/$(TestOutFile)

check: chktex $(srcdir)/$(TestOutFile) chktexrc
	@echo ">>> Testing that checking algorithms work correctly..."
	@-rm -f chktest
	$(MAKETEST) 1> chktest
	@if cmp -s chktest $(srcdir)/$(TestOutFile); then \
		echo ">>> OK!"; \
		rm -f chktest; \
	else \
		echo "***WARNING***"; \
		echo "Problems when checking compilation. This may or may not"; \
		echo "be a problem; anyway, I'm giving you a diff from what the"; \
		echo "results were *supposed* to be..."; \
		diff -u $(srcdir)/$(TestOutFile) chktest; \
	fi
	$(srcdir)/tests/run-tests.sh `pwd` "$(srcdir)"


chktex: $(OBJS)
	$(CC) $(LDFLAGS) -o chktex $(OBJS) $(LIBS)

install: chktex ChkTeX.dvi
	$(MKDIR_P) $(DESTDIR)$(bindir)
	for program in chktex $(BUILT_SCRIPTS); do \
		$(INSTALL_PROGRAM) $$program $(DESTDIR)$(bindir); \
	done
	for program in $(SCRIPTS); do \
		$(INSTALL_PROGRAM) $(srcdir)/$$program $(DESTDIR)$(bindir); \
	done
	$(MKDIR_P) $(DESTDIR)$(sysconfdir)
	$(INSTALL_DATA) $(srcdir)/chktexrc $(DESTDIR)$(sysconfdir)
	if (eval echo "$(BUILT_SCRIPTS)") | egrep deweb >/dev/null 2>&1; then \
		$(MKDIR_P) $(DESTDIR)$(mandir)/man1; \
                cp $(srcdir)/deweb.1 $(DESTDIR)$(mandir)/man1; \
	fi



uninstall:
	for program in chktex $(SCRIPTS) $(BUILT_SCRIPTS); do \
		rm -f $(DESTDIR)$(bindir)/$$program; \
	done
	rm -f $(DESTDIR)$(sysconfdir)/chktexrc  $(DESTDIR)$(mandir)/man1/deweb.1

test:
	chktex -v2 -mall $(srcdir)/Test.tex | less -r

indent:
	indent -npsl -bli0 -npcs -nut -i4 $(SOURCEFILES)

mostlyclean: clean

clean:
	rm -rf $(CLEAN) $(BUILT_DIST) $(DISTDIR).tar.gz \
	  *.aux *.log *.pdf *.dvi *.ps \
	  chktex HTML rme chktest

distclean: clean
	rm -rf $(CONFIG_DIST) *.cache *.status *.log *.tar.gz \
	  deweb Makefile autom4te.cache config.h

maintainer-clean: distclean
	rm -rf *.rme install-sh config.guess config.sub aclocal.m4 \
	  configure missing rmeheader stamp-h mkinstalldirs tags

dvi: ChkTeX.dvi

pdf: ChkTeX.pdf

ifneq ($(LATEX2HTML),)
html: ChkTeX.tex MakeHTML.pl
	-rm -r HTML
	$(MKDIR_P) HTML
	$(PERL5) $(srcdir)/MakeHTML.pl ChkTeX.tex > HTML/ChkTeX.tex
	cd HTML; $(LATEX2HTML) ChkTeX.tex
	$(PERL5) -i -pe 's%</code> %</code>%gi;s%\s+([.,?!])%$$1%g;' HTML/ChkTeX/*.html

README: ChkTeX.tex rmeheader MakeHTML.pl
	rm -rf rme
	$(MKDIR_P) rme
	$(PERL5) $(srcdir)/MakeHTML.pl ChkTeX.tex > rme/ChkTeX.tex
	cd rme; $(LATEX2HTML) -split 0 ChkTeX.tex
	$(PERL5) -i -pe 's%L<SUP><SMALL>A</SMALL></SUP>%La%g;s%T<SMALL>E</SMALL>X%TeX%g;s%<SUB>(.*)</SUB>%$$1%g' rme/ChkTeX/*.html
	$(PERL5) -i -pe 's%</code> %</code>%gi;s%\s+([.,?!])%$$1%g;' rme/ChkTeX/*.html
	$(LYNX) -dump rme/ChkTeX/ChkTeX.html > rme/ChkTeX.rme
	cp rmeheader README
	$(PERL5) -e 'undef $$/;$$_=<>;($$_)=/(.*INTRODUCTION(.|\n)*?)[ \t]+ABOUT THIS DOCUMENT/i;s/[ \t]+\n/\n/g;s/\n\n\n/\n/g;s/\[\d+\]//g;print;' rme/ChkTeX.rme >> README
	rm -rf rme
else
html README:
	@echo "latex2html is unavailable on this system, cant create target $@."; exit 1
endif

###################### AUTOCONF REMAKING ################################

$(srcdir)/configure: configure.ac aclocal.m4
	cd $(srcdir) && autoconf

#autoheader might not change config.h.in, so touch a stamp file.
$(srcdir)/config.h.in: stamp-h.in
$(srcdir)/stamp-h.in: configure.ac aclocal.m4
	cd $(srcdir) && autoheader
	echo timestamp > $(srcdir)/stamp-h.in

config.h: stamp-h
stamp-h: config.h.in config.status
	./config.status

ChkTeX.tex: ChkTeX.tex.in
	./config.status ChkTeX.tex

Makefile: Makefile.in config.status
	./config.status

config.status: configure
	./config.status --recheck

###################### INDIVIDUAL DEPENDENCIES ##########################

%.doc: %.1
	$(GROFF) $< > $@

ChkTeXRC.tex: chktexrc.in MakeChkTeXRC.pl
	 $(PERL5) $(srcdir)/MakeChkTeXRC.pl --latex $(srcdir)/chktexrc.in > ChkTeXRC.tex

chktexrc: chktexrc.in  MakeChkTeXRC.pl
	 $(PERL5) $(srcdir)/MakeChkTeXRC.pl --chktexrc $(srcdir)/chktexrc.in > chktexrc


ChkTeX.dvi: ChkTeX.tex ChkTeXRC.tex
ifdef LATEX
	$(LATEX) ChkTeX.tex
else
	echo "No latex program found by configure"
	false
endif

ChkTeX.ps: ChkTeX.dvi
	$(DVIPS) -o ChkTeX.ps ChkTeX.dvi

ifdef PDFLATEX
ChkTeX.pdf: ChkTeX.tex ChkTeXRC.tex
	$(PDFLATEX) -interaction=nonstopmode ChkTeX.tex
else
ChkTeX.pdf: ChkTeX.ps
	$(PS2PDF) $< $@
endif

cover:
	-./chktex -h
	-./chktex Test.tex
	-./chktex -v2 -t -o tmptmptmp <Test.tex
	-./chktex -v2 -t -o tmptmptmp Test.tex
	-./chktex Test.tex -v
	-./chktex Test.tex -v0
	-./chktex Test.tex -v1
	-./chktex Test.tex -v2
	-./chktex Test.tex -v3
	-./chktex Test.tex -v4
	-./chktex -t -v0s::: Test.tex -x
	-./chktex -p FOO Test.tex
	-./chktex -t Test.tex
	-./chktex -o tmptmptmp -o tmptmptmptmp Test.tex
	-./chktex -l t:faultrc test.tex
	-./chktex -e30w22n1 Test.tex
	-./chktex -w33e-n1 Test.tex
	-./chktex -i
	-./chktex -v2 -t -o tmptmptmp <Test.tex
	-./chktex -I Test.tex
	-./chktex -rd2 Test.tex
	-./chktex -gd2 Test.tex
	-./chktex -f "*N\
Between: %b*N\
Column: %c*N\
Length: %d*N\
File: %f*N\
%iInverse%I*N\
Kind: %k*N\
Line: %l*N\
Msg: %m*N\
Num: %n*N\
Und: %u*N\
Pre:  %r*N\
Str:  %s*N\
Post: %t*N\
*N\
%k in %f line %l: %m*N\
%r%i%s%I%t*N\
%u*N\
*N" Test.tex
	-./chktex -o tmptmptmp -r -d2 Test.tex
	-./chktex -qv0 Test.tex
	-./chktex -w30 Test.tex
	-./chktex -g --localrc=.testrc -d2 Test.tex
	for file in $(CSOURCES); do gcov $(GCOVOPTS) $$file; done

valgrind: chktex
	valgrind --tool=memcheck --leak-check=full chktex -mall -r -g0 -lchktexrc -v5 Test.tex | grep ^[-=][-=]
