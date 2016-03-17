#!/bin/sh
for subdir in js perl
do
    echo "Build subdirectory: $subdir"
	cd $subdir
	make
	cd ..
done
