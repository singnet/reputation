package controller

import (
	"context"
	"fmt"
	"log"
	"math/big"
	"strings"

	ethereum "github.com/ethereum/go-ethereum"
	"github.com/ethereum/go-ethereum/accounts/abi"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/ethclient"

	"github.com/tiero/reputation/adapter/database"
	"github.com/tiero/reputation/adapter/resources/contracts/mpe"
)

//Network config struct
type Network struct {
	RPCEndpoint     string
	DeployedAddress common.Address
	startingBlock   int64
	endingBlock     int64
}

//Escrow is escrow struct
type Escrow struct {
	ContractName    string
	ABI             abi.ABI
	Client          *ethclient.Client
	startingBlock   int64
	DeployedAddress common.Address
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

var channelLog = &database.ChannelLog{}

//New is a function to populate an instance of an Escrow adapter
func (e *Escrow) New(networkKey string) error {
	// Ethereum client
	currentNetwork := networks[networkKey]

	client, err := ethclient.Dial(currentNetwork.RPCEndpoint)
	if err != nil {
		return err
	}

	abiDefinition, err := abi.JSON(strings.NewReader(string(mpe.MpeABI)))
	if err != nil {
		return err
	}

	e.ContractName = "MultiPartyEscrow"
	e.ABI = abiDefinition
	e.Client = client
	e.startingBlock = currentNetwork.startingBlock
	e.DeployedAddress = currentNetwork.DeployedAddress

	return nil
}

//Start func
func (e *Escrow) Start() {
	//Start db
	channelLog.New()
	//Fisrt get the current block
	header, err := e.Client.BlockByNumber(context.Background(), nil)
	if err != nil {
		log.Fatal(err)
	}

	lastBlock := header.Number

	// Compare the block checkpoint in local database
	if lastBlock.Cmp(channelLog.LastBlock) == 1 {
		logs := e.getPastEvents(channelLog.LastBlock)
		e.update(logs)
	}
}

//GetPastEvents func
func (e *Escrow) getPastEvents(startingBlock *big.Int) []types.Log {
	query := ethereum.FilterQuery{
		FromBlock: startingBlock,
		Addresses: []common.Address{e.DeployedAddress},
	}

	logs, err := e.Client.FilterLogs(context.Background(), query)

	if err != nil {
		log.Fatal(err)
	}

	return logs
}

func (e *Escrow) update(logs []types.Log) {
	for _, vLog := range logs {
		//fmt.Printf("Log Block Number: %d\n", vLog.BlockNumber)
		//fmt.Printf("Log Index: %d\n", vLog.Index)

		blockNumber := big.NewInt(int64(vLog.BlockNumber))
		block, err := e.Client.BlockByNumber(context.Background(), blockNumber)
		if err != nil {
			log.Fatal(err)
		}
		blockTimestamp := block.Time().Int64()

		switch vLog.Topics[0].Hex() {
		case channelClaimSigHash.Hex():

			var channelClaimEvent ChannelClaim

			err := e.ABI.Unpack(&channelClaimEvent, "ChannelClaim", vLog.Data)
			if err != nil {
				log.Fatal(err)
			}

			channelClaimEvent.ChannelId = vLog.Topics[1].Big()
			channelClaimEvent.Recipient = common.HexToAddress(vLog.Topics[2].Hex())

			openTime := int64(0)
			closeTime := blockTimestamp

			nextChannel := &database.Channel{
				channelClaimEvent.ChannelId,
				channelClaimEvent.Recipient,
				channelClaimEvent.Recipient,
				channelClaimEvent.ClaimAmount,
				openTime,
				closeTime,
			}

			channelLog.Append(nextChannel, blockNumber)
			/* fmt.Printf("\n\nChannel Claim\n\n")
			fmt.Printf("ChannelID: %s\n", channelClaimEvent.ChannelId)
			fmt.Printf("Recipient: %s\n", channelClaimEvent.Recipient.Hex())
			fmt.Printf("Claim Amount: %s\n", )

			*/

		case channelSenderClaimSigHash.Hex():
			//fmt.Println("Channel Sender Claim")
			var channelSenderClaimEvent ChannelSenderClaim
			err := e.ABI.Unpack(&channelSenderClaimEvent, "ChannelSenderClaim", vLog.Data)
			if err != nil {
				log.Fatal(err)
			}

			fmt.Printf("\n\nChannel Sender Claim\n\n")
			channelSenderClaimEvent.ChannelId = vLog.Topics[1].Big()

			fmt.Printf("ChannelID: %s\n", channelSenderClaimEvent.ChannelId)
			fmt.Printf("Claim Amount: %s\n", channelSenderClaimEvent.ClaimAmount)
		case channelExtendSigHash.Hex():
			//fmt.Println("Channel Extend")
		case channelAddFundsSigHash.Hex():
			//fmt.Println("Channel Add Funds"
		case channelOpenSigHash.Hex():
			/*
				var channelOpenEvent ChannelOpen
				err := mpeAbi.Unpack(&channelOpenEvent, "ChannelOpen", vLog.Data)
				if err != nil {
					log.Fatal(err)
				}

				channelOpenEvent.Sender = common.HexToAddress(vLog.Topics[1].Hex())
				channelOpenEvent.Recipient = common.HexToAddress(vLog.Topics[2].Hex())

				fmt.Printf("\n\nChannel Open \n\n")
				fmt.Printf("ChannelID: %s\n", channelOpenEvent.ChannelId)
				fmt.Printf("Sender: %s\n", channelOpenEvent.Sender.Hex())
				fmt.Printf("Recipient: %s\n", channelOpenEvent.Recipient.Hex())
				fmt.Printf("Amount: %s\n", channelOpenEvent.Amount)
				fmt.Printf("Expiration: %s\n", channelOpenEvent.Expiration) */

		}

	}
}
