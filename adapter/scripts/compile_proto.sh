#!/bin/bash
set -e

cd adapter/resources/protos
python -m grpc_tools.protoc -I .  --python_out=. --grpc_python_out=. adapter_service.proto