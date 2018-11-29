package database

import (
	"math/big"

	"github.com/ethereum/go-ethereum/common"
)

//ChannelLog type
type ChannelLog struct {
	Log       []*Channel
	Index     map[*big.Int]int
	LastBlock *big.Int
}

//Channel type
type Channel struct {
	ChannelId   *big.Int
	Sender      common.Address
	Recipient   common.Address
	ClaimAmount *big.Int
	OpenTime    int64
	CloseTime   int64
}

//New function
func (l *ChannelLog) New() {
	l.Log = []*Channel{}
	l.Index = make(map[*big.Int]int)
	l.LastBlock = big.NewInt(0)
}

//Append function
func (l *ChannelLog) Append(nextChannel *Channel, blockNumber *big.Int) {
	channelID := nextChannel.ChannelId
	position := len(l.Log)
	l.Log = append(l.Log, nextChannel)
	l.Index[channelID] = position
	l.LastBlock = blockNumber
}
