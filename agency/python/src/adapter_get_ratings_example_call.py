import grpc 
import adapter_service_pb2
import adapter_service_pb2_grpc

channel = grpc.insecure_channel('localhost:8080')
stub = adapter_service_pb2_grpc.RatingServiceStub(channel)
summary = stub.GetRatings(adapter_service_pb2.BlockInterval(open_time=0,close_time=0))

print(summary.ratings)