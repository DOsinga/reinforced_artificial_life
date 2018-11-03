#!/bin/bash
git ls-files \
  | egrep '\.py$' \
  | xargs black --line-length 99 --skip-string-normalization $*
