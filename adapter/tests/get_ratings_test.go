package main

import (
	"context"
	"log"
	"testing"

	pb "github.com/tiero/reputation/adapter/resources/protos"
	"google.golang.org/grpc"
)

func TestGetRatings(t *testing.T) {

	conn, err := grpc.Dial("localhost:8080", grpc.WithInsecure())
	if err != nil {
		log.Panic(err)
	}
	defer conn.Close()

	client := pb.NewRatingServiceClient(conn)

	ratingSummary, err := client.GetRatings(context.Background(), &pb.BlockInterval{OpenTime: 0, CloseTime: 0})
	if err != nil {
		log.Panic(err)
	}

	log.Println(ratingSummary.Ratings)

}
