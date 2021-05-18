#!/bin/bash
for f in *_10000000.xml
    do cyclus -i $f -o ${f%%.*}.sqlite
done
