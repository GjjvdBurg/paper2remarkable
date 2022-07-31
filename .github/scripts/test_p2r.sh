#!/bin/bash
#
# Setup environment and run unit tests for paper2remarkable
#
# After Travis effectively removed support for open source projects I've 
# decided to capture all testing facilities in a single script, to ensure we 
# can more easily move between CI providers.
#
# This script is intended to be run inside a virtual machine (or equivalent) 
# that runs Ubuntu Xenial. It will affect the system installed packages.
#
# Author: G.J.J. van den Burg
# Date: 2020-12-28
#

set -e -u -x -o pipefail

NODE_VERSION="v12.18.1"
NVM_VERSION="v0.36.0"

echo "Setting up environment"
echo "::group::Updating system ..."

sudo apt-get update

echo "::group::Installing system dependencies for paper2remarkable"

sudo apt-get install ghostscript pdftk poppler-utils qpdf

echo "::group::Installing nvm ..."

sudo apt-get install build-essential libssl-dev -y

curl -o- "https://raw.githubusercontent.com/nvm-sh/nvm/${NVM_VERSION}/install.sh" | bash

source ~/.nvm/nvm.sh

echo "::group::Installing node version ${NODE_VERSION}"

nvm install ${NODE_VERSION}

echo "::group::Activating node version ${NODE_VERSION}"

nvm use ${NODE_VERSION}

echo "::group::Installing pre-commit"

pip install pre-commit

echo "::group::Install package"

pip install --upgrade --upgrade-strategy eager -e .[test]

echo "::group::Run pre-commit"

pre-commit run --all-files --show-diff-on-failure

echo "::group::Check if ReadabiliPy was installed with Node support"

python -c 'from readabilipy.simple_json import have_node; print(f"Have node: {have_node()}")'

echo "::group::Run unit tests"

green -vv -a ./tests
