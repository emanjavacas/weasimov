#! /usr/bin/bash

# deploy ucto with quote detection to segment each document
# into paragraphs, sentences, and word tokens.

subdir=$1

for f in data/$subdir/*.txt
do
    ucto -L nl -n -Q "$f" > "data/tokenized/${f##*/}"
done;
