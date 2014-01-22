#!/bin/sh

mkdir -p build
cd build
cmake -DITK_DIR:PATH=~/bin/ITK ..
make -j6
