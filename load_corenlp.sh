#!/bin/bash
dir=$(pwd)
corenlp_dir="$dir/stanford-corenlp"
export CLASSPATH="$corenlp_dir/*"
echo "Done."
