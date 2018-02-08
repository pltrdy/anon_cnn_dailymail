#!/bin/bash

dir=$(pwd)
wget http://nlp.stanford.edu/software/stanford-corenlp-full-2018-01-31.zip
unzip stanford-corenlp-full-2018-01-31.zip

java -cp "$dir/stanford-corenlp-full-2018-01-31/*" -Xmx2g edu.stanford.nlp.pipeline.StanfordCoreNLP -file inputFile
