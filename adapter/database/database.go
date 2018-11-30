package database

import (
	"log"
	"math/big"

	"database/sql"

	"github.com/ethereum/go-ethereum/common"
	_ "github.com/lib/pq"
)

//ChannelLog type
type ChannelLog struct {
	Log       []*Channel
	Index     map[*big.Int]int
	LastBlock uint64
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

//Init func
func Init() *sql.DB {
	connStr := "user=postgres dbname=postgres sslmode=disable"
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal(err)
	}

	return db
}

//New function
func (l *ChannelLog) New() {
	l.Log = []*Channel{}
	l.Index = make(map[*big.Int]int)
	l.LastBlock = uint64(0)
}

//Append function
func (l *ChannelLog) Append(nextChannel *Channel, blockNumber uint64) {
	channelID := nextChannel.ChannelId
	position := len(l.Log)
	l.Log = append(l.Log, nextChannel)
	l.Index[channelID] = position
	l.LastBlock = blockNumber
}
