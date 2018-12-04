package database

import (
	"log"
	"math/big"

	"database/sql"

	"github.com/ethereum/go-ethereum/common"
	_ "github.com/lib/pq"
	"github.com/pkg/errors"
)

//ChannelLog type
type ChannelLog struct {
	DB        *sql.DB
	Log       []*Channel
	Index     map[*big.Int]int
	LastBlock uint64
}

//Channel type
type Channel struct {
	ChannelId   *big.Int
	Nonce       *big.Int
	Sender      common.Address
	Recipient   common.Address
	ClaimAmount *big.Int
	OpenTime    int64
	CloseTime   int64
}

//GetAll func
func (l *ChannelLog) GetAll() {
	queryStmt, err := l.DB.Prepare("SELECT * FROM channel;")

	if err != nil {
		log.Fatal(err)
	}

	rows, err := queryStmt.Query()
	defer rows.Close()

	var (
		channelId int64
		nonce     int64
		sender    string
		recipient string
		amount    int64
		openTime  int64
		closeTime int64
	)
	for rows.Next() {

		err := rows.Scan(&channelId, &nonce, &sender, &recipient, &amount, &openTime, &closeTime)
		if err != nil {
			log.Fatal(err)
		}

		nextChannel := &Channel{
			big.NewInt(channelId),
			big.NewInt(nonce),
			common.HexToAddress(sender),
			common.HexToAddress(recipient),
			big.NewInt(amount),
			openTime,
			closeTime,
		}

		l.Append(nextChannel, uint64(closeTime))

	}

	return
}

//Insert is a func
func (l *ChannelLog) Insert(nc *Channel) error {

	const qry = "INSERT INTO channel (channel_id, nonce, sender, recipient, amount, open_time, close_time) VALUES ($1,$2,$3,$4,$5,$6);"

	_, err := l.DB.Exec(qry, nc.ChannelId.Int64(), nc.Sender.String(), nc.Recipient.String(), nc.ClaimAmount.Int64(), nc.OpenTime, nc.CloseTime)
	if err != nil {
		log.Fatal(err)
		return err
	}

	return nil

}

//New function
func (l *ChannelLog) New() {

	connStr := "user=postgres password=postgres dbname=postgres sslmode=disable"
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal(err)
	}

	if err = db.Ping(); err != nil {
		err = errors.Wrapf(err, "Couldn't ping postgre database")
		return
	}

	l.DB = db
	l.Log = []*Channel{}
	l.Index = make(map[*big.Int]int)
	l.LastBlock = uint64(0)

	return
}

//Append function
func (l *ChannelLog) Append(nextChannel *Channel, blockNumber uint64) {
	channelID := nextChannel.ChannelId
	position := len(l.Log)
	l.Log = append(l.Log, nextChannel)
	l.Index[channelID] = position
	l.LastBlock = blockNumber
}
