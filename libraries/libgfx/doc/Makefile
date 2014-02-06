DOC_SOURCE_DIR:=$(PWD)/..
DOC_MODULE:=libgfx
DOC_MAIN_SGML_FILE:=libgfx.xml
MKDB_OPTIONS:=--xml-mode
HFILE_GLOB:=$(DOC_SOURCE_DIR)/*.h
CFILE_GLOB:=$(DOC_SOURCE_DIR)/*.c $(DOC_SOURCE_DIR)/*.cpp

TARGET_DIR=/usr/local/share/arduino/libraries/libgfx/doc
AM_DEFAULT_VERBOSITY=0
AM_v_at=
GTKDOC_REBASE=gtkdoc-rebase
INSTALL_DATA=@echo INSTALL:

EXTRA_CLEANFILES=$(DOC_MODULE).types $(DOC_MODULE)-sections.txt

all: docs
clean: distclean-local
	@rm -rf $(CLEANFILES) $(EXTRA_CLEANFILES)

include gtk-doc.notmpl-flat.make

.PHONY: clean
