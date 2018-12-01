package main

import (
	"flag"
	"log"

	"github.com/tiero/reputation/adapter/controller"
)

func main() {

	//Flags config
	networkKey := flag.String("network", "kovan", "network. One of {mainnet, ropsten, kovan}")

	//New Escrow Instance
	escrow := &controller.Escrow{}
	err := escrow.New(*networkKey)
	if err != nil {
		log.Fatal(err)
	}

	escrow.Start()

}
