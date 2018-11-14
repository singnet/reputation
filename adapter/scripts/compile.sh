#!/bin/sh
PARENT_PATH=$(dirname $(cd $(dirname $0); pwd -P))

cd $PARENT_PATH/node_modules/singularitynet-platform-contracts
npm install
npm run compile

