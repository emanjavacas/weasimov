#! /usr/bin/bash

# deploy ucto with quote detection to segment each document
# into paragraphs, sentences, and word tokens.

for f in data/txt/*.txt
  do
      ucto -L nl -n -Q "$f" > "../tokenized/$f"
  done;
