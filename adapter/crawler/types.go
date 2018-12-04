package controller

import (
	"math/big"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/crypto"
)

var (
	channelOpenSigHash        = crypto.Keccak256Hash([]byte("ChannelOpen(uint256,address,address,bytes32,address,uint256,uint256)"))
	channelClaimSigHash       = crypto.Keccak256Hash([]byte("ChannelClaim(uint256,address,uint256,uint256,uint256)"))
	channelSenderClaimSigHash = crypto.Keccak256Hash([]byte("ChannelSenderClaim(uint256,uint256)"))
	channelExtendSigHash      = crypto.Keccak256Hash([]byte("ChannelExtend(uint256,uint256)"))
	channelAddFundsSigHash    = crypto.Keccak256Hash([]byte("ChannelAddFunds(uint256,uint256)"))
)

type ChannelOpen struct {
	ChannelId  *big.Int
	Sender     common.Address
	Recipient  common.Address
	GroupId    []byte
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
	KeepAmpount    *big.Int
}

//ChannelSenderClaim event struct
type ChannelSenderClaim struct {
	ChannelId   *big.Int
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
