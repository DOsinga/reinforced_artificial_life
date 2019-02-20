#!/bin/bash
git ls-files \
  | egrep '\.py$' \
  | xargs black --line-length 120 --skip-string-normalization $*
