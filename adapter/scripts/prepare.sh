##!/bin/bash
# Install go ethereum 
go get -u -x github.com/ethereum/go-ethereum
cd $GOPATH/src/github.com/ethereum/go-ethereum/
make
make devtools


