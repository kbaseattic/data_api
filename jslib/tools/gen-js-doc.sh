#!/bin/bash

# Builds the js docs into a location of your choosing...

#PACKAGE=ui-common
TOPDIR=`pwd`
#FAKEDEPLOY=$TOPDIR/../fake-deploy
JSDOCSDIR=src/htdocs/jsdocs
SRCDIR=src


# remove the doc dir?

jsdoc -d $JSDOCSDIR -p $SRCDIR/js/Taxon.js $SRCDIR/docs/types.js
