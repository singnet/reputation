package main

import (
	"flag"
	"log"

	"github.com/singnet/reputation/adapter/server"
	crawler "github.com/singnet/reputation/adapter/crawler"

)

func main() {

	//Flags config
	networkKey := flag.String("network", "kovan", "network. One of {mainnet, ropsten, kovan}")

	//New Escrow Instance
	escrow := &crawler.Escrow{}
	err := escrow.New(*networkKey)
	if err != nil {
		log.Fatal(err)
	}

	//escrow.Start()

	// Grpc Server
	server.Start()

}
