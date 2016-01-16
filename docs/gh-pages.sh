#!/bin/bash

set -e

DOCS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_DIR=`dirname $DOCS_DIR`
TMP_DIR=`mktemp -d`

# Build it
make html

# Clone to a temporary repo and commit the newly built HTML
pushd $TMP_DIR
git clone $REPO_DIR $TMP_DIR
git checkout gh-pages
cp -R $DOCS_DIR/build/html/* $TMP_DIR
git add -A .
git commit -m "Update built docs"
popd

# Update our local gh-pages by fetching the remote gh-pages
git fetch $TMP_DIR gh-pages:gh-pages

# Delete the temporary repo
rm -rf $TMP_DIR

# You still need to push the gh-pages branch at this point. The branch
# should be up to date, though.
