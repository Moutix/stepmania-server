#!/bin/sh

set -e

cd docs && make apidoc && cd ..
git checkout gh-pages
rm -rf _build _sources _static _download
git checkout master docs
git reset HEAD
cd docs && make html && cd ..
mv -fv docs/_build/html/* ./
rm -rf docs _build
git add -A
git commit -m "Generated gh-pages for `git log master -1 --pretty=short --abbrev-commit`"
git push origin gh-pages
git checkout master
