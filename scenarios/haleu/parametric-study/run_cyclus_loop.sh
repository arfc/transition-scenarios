#!/bin/bash
for f in *_1e7.xml
    do cyclus -i $f -o ${f%%.*}.sqlite
done
