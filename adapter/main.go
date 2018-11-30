package main

import (
	"flag"
	"log"

	"github.com/tiero/reputation/adapter/controller"
	db "github.com/tiero/reputation/adapter/database"
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

	db := db.Init()

	err = db.Ping()
	if err != nil {
		log.Fatal(err)
	}
	//escrow.Start()
	//Debug-only
	escrow.GetInfo()

}
