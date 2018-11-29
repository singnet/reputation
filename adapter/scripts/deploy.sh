#!/bin/sh
PARENT_PATH=$(dirname $(cd $(dirname $0); pwd -P))

cd $PARENT_PATH/node_modules/singularitynet-platform-contracts
npm run deploy
cp -R $PARENT_PATH/node_modules/singularitynet-platform-contracts/build/ $PARENT_PATH/resources/build/ 
