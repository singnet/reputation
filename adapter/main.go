package main

//0x8D9D080427f73e9f42bA183F0b7A4Dd770BE33A8

import (
	"context"
	"flag"
	"fmt"
	"log"
	"math/big"

	ethereum "github.com/ethereum/go-ethereum"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/ethclient"
)

//Network config struct
type Network struct {
	RPCEndpoint     string
	DeployedAddress common.Address
}

var networks = map[string]Network{
	"kovan": Network{
		"https://kovan.infura.io",
		common.HexToAddress("0x385036D6cd8Cf6A8749d5Df7f716F0341E1c13B1"),
	},
	"ropsten": Network{
		"https://ropsten.infura.io",
		common.HexToAddress("0xAF5e3b8CF89815F24A12D45D4758D87257249778"),
	},
}

const (
	startingBlock int64 = 4429391
)

func main() {
	networkKey := flag.String("network", "ropsten", "network. One of {mainnet, ropsten, kovan}")
	currentNetwork := networks[*networkKey]

	client, err := ethclient.Dial(currentNetwork.RPCEndpoint)
	if err != nil {
		log.Fatal(err)
	}

	query := ethereum.FilterQuery{
		FromBlock: big.NewInt(startingBlock),
		Addresses: []common.Address{currentNetwork.DeployedAddress},
	}

	logs, err := client.FilterLogs(context.Background(), query)
	if err != nil {
		log.Fatal(err)
	}

	for _, vLog := range logs {
		fmt.Println(vLog.TxHash.Hex())
	}

	/*

		mpeInstance, err := mpe.NewMpe(mpeAddress, client)
			if err != nil {
				log.Fatal(err)
			}

			fmt.Println(mpeInstance.Token(nil))
	*/

}
