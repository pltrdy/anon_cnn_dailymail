#!/bin/bash
set -e

wget http://nlp.stanford.edu/software/stanford-corenlp-full-2018-01-31.zip
unzip stanford-corenlp-full-2018-01-31.zip

ln -s stanford-corenlp-full-2018-01-31 ./stanford-corenlp
echo "Done."
