##!/bin/bash

PARENT_PATH=$(dirname $(cd $(dirname $0); pwd -P))
cd $PARENT_PATH

ARTIFACT="$PARENT_PATH/node_modules/singularitynet-platform-contracts/build/contracts/MultiPartyEscrow.json"

mkdir -p resources/contracts
mkdir -p resources/abi

node_modules/underscore-cli/bin/underscore select .abi --in $ARTIFACT --out $PARENT_PATH/resources/abi/MultiPartyEscrow.json  --outfmt text
$GOPATH/bin/abigen --abi=resources/abi/MultiPartyEscrow.json --pkg=mpe --out=resources/contracts/MultiPartyEscrow.go

echo "Moved go contracts packages in resources/contracts folder"