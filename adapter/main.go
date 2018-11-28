package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"math/big"

	ethereum "github.com/ethereum/go-ethereum"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/crypto"
	"github.com/ethereum/go-ethereum/ethclient"
)

type ChannelOpen struct {
	ChannelId  *big.Int
	Sender     common.Address
	Recipient  common.Address
	GroupId    [32]byte
	Signer     common.Address
	Amount     *big.Int
	Expiration *big.Int
}

//ChannelClaim event struct
type ChannelClaim struct {
	ChannelId      *big.Int
	Recipient      common.Address
	ClaimAmount    *big.Int
	SendBackAmount *big.Int
	KeepAmount     *big.Int
}

//ChannelSenderClaim event struct
type ChannelSenderClaim struct {
	ChannelID   *big.Int
	ClaimAmount *big.Int
}

//ChannelExtend event struct
type ChannelExtend struct {
	ChannelId     *big.Int
	NewExpiration *big.Int
}

//ChannelAddFunds event struct
type ChannelAddFunds struct {
	ChannelId *big.Int
	NewFunds  *big.Int
}

//Network config struct
type Network struct {
	RPCEndpoint     string
	DeployedAddress common.Address
	startingBlock   int64
	endingBlock     int64
}

var networks = map[string]Network{
	"kovan": Network{
		"https://kovan.infura.io",
		common.HexToAddress("0xdd4292864063d0DA1F294AC65D74d55a44F4766C"),
		9424242,
		9508189,
	},
	"ropsten": Network{
		"https://ropsten.infura.io",
		common.HexToAddress("0xAF5e3b8CF89815F24A12D45D4758D87257249778"),
		4429391,
		0,
	},
}

var (
	channelOpenSigHash        = crypto.Keccak256Hash([]byte("ChannelOpen(uint256,address,address,bytes32,address,uint256,uint256)"))
	channelClaimSigHash       = crypto.Keccak256Hash([]byte("ChannelClaim(uint256,address,uint256,uint256,uint256)"))
	channelSenderClaimSigHash = crypto.Keccak256Hash([]byte("ChannelSenderClaim(uint256,uint256)"))
	channelExtendSigHash      = crypto.Keccak256Hash([]byte("ChannelExtend(uint256,uint256)"))
	channelAddFundsSigHash    = crypto.Keccak256Hash([]byte("ChannelAddFunds(uint256,uint256)"))
)

func main() {
	networkKey := flag.String("network", "kovan", "network. One of {mainnet, ropsten, kovan}")
	currentNetwork := networks[*networkKey]

	client, err := ethclient.Dial(currentNetwork.RPCEndpoint)
	if err != nil {
		log.Fatal(err)
	}

	query := ethereum.FilterQuery{
		FromBlock: big.NewInt(currentNetwork.startingBlock),
		ToBlock:   big.NewInt(currentNetwork.endingBlock),
		Addresses: []common.Address{currentNetwork.DeployedAddress},
	}

	logs, err := client.FilterLogs(context.Background(), query)
	if err != nil {
		log.Fatal(err)
	}

	/* mpeAbi, err := abi.JSON(strings.NewReader(string(mpe.MpeABI)))
	if err != nil {
		log.Fatal(err)
	} */

	for _, vLog := range logs {
		/*
			event := ChannelOpen{}
			err := mpeAbi.Unpack(&event, "ChannelOpen", vLog.Data)
		*/

		//fmt.Printf("Log Block Number: %d\n", vLog.BlockNumber)
		//fmt.Printf("Log Index: %d\n", vLog.Index)

		switch vLog.Topics[0].Hex() {
		case channelOpenSigHash.Hex():
			fmt.Println("Channel Open")
		case channelClaimSigHash.Hex():
			fmt.Println("Channel Claim")
		case channelSenderClaimSigHash.Hex():
			fmt.Println("Channel Sender Claim")
		case channelExtendSigHash.Hex():
			fmt.Println("Channel Extend")
		case channelAddFundsSigHash.Hex():
			fmt.Println("Channel Add Funds")

		}

	}
}
