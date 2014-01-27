#!/bin/sh

mkdir -p build
cd build
cmake -DCMAKE_BUILD_TYPE:STRING=Release -DITK_DIR:PATH=~/bin/ITK ..
make
