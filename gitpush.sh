#! /bin/bash

cat ~/token.txt

git add --all .
git commit -m "auto update from gitpush.sh - tony"
git push
