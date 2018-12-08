/*
 *
 * Copyright 2015 gRPC authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

//go:generate protoc -I ../routeguide --go_out=plugins=grpc:../routeguide ../routeguide/route_guide.proto

// Package main implements a simple gRPC server that demonstrates how to use gRPC-Go libraries
// to perform unary, client streaming, server streaming and full duplex RPCs.
//
// It implements the route guide service whose definition can be found in routeguide/route_guide.proto.
package server

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net"

	"google.golang.org/grpc"

	"google.golang.org/grpc/credentials"
	"google.golang.org/grpc/testdata"

	"github.com/singnet/reputation/adapter/database"
	pb "github.com/singnet/reputation/adapter/resources/protos"
)

var (
	tls      = flag.Bool("tls", false, "Connection uses TLS if true, else plain TCP")
	certFile = flag.String("cert_file", "", "The TLS cert file")
	keyFile  = flag.String("key_file", "", "The TLS key file")
	port     = flag.Int("port", 8080, "The server port")
)

var channelLog = &database.ChannelLog{}

type adapterService struct {
	version    string
	channelLog *database.ChannelLog
}

func newServer() *adapterService {
	s := &adapterService{}
	//Start db
	channelLog.New()
	s.channelLog = channelLog
	return s
}

func (s *adapterService) GetRatings(ctx context.Context, interval *pb.BlockInterval) (*pb.RatingSummary, error) {

	ratings := []*pb.Rating{}
	s.channelLog.GetAll()
	for _, channel := range s.channelLog.Log {
		currInterval := &pb.BlockInterval{}
		currInterval.OpenTime = channel.OpenTime
		currInterval.CloseTime = channel.CloseTime
		nextRating := &pb.Rating{
			ChannelId: channel.ChannelId.Int64(),
			Nonce:     channel.Nonce.Int64(),
			Consumer:  channel.Sender.Hex(),
			Provider:  channel.Recipient.Hex(),
			Interval:  interval,
			Amount:    channel.ClaimAmount.Int64(),
		}
		ratings = append(ratings, nextRating)
	}
	summary := &pb.RatingSummary{Ratings: ratings}
	return summary, nil
}

//Start is a func
func Start() {
	flag.Parse()
	lis, err := net.Listen("tcp", fmt.Sprintf("localhost:%d", *port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	var opts []grpc.ServerOption
	if *tls {
		if *certFile == "" {
			*certFile = testdata.Path("server1.pem")
		}
		if *keyFile == "" {
			*keyFile = testdata.Path("server1.key")
		}
		creds, err := credentials.NewServerTLSFromFile(*certFile, *keyFile)
		if err != nil {
			log.Fatalf("Failed to generate credentials %v", err)
		}
		opts = []grpc.ServerOption{grpc.Creds(creds)}
	}
	fmt.Println("Running at localhost:", *port)
	grpcServer := grpc.NewServer(opts...)
	pb.RegisterRatingServiceServer(grpcServer, newServer())
	grpcServer.Serve(lis)
}
