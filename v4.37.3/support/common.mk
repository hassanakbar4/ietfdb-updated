TOP ?= .
UP  = ..

PKG  ?= $(shell grep Package DEBIAN/control | cut -d " " -f2)
WEEK ?= $(shell date +%Y%V)
REV  :=$(shell date +%Y%m%d.t%H%M)
VER  ?= 3.0.$(REV)
DEB  ?= $(PKG)_$(VER).deb
INCOMING ?= sg1@galaxy.gatineau.credil.org:/home/sg1/incoming
