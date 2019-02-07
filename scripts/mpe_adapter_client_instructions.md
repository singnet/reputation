
* Compile [Protocol Buffers](https://developers.google.com/protocol-buffers/docs/downloads) and generate Python stubs from proto defintiion
```bash
$ ./scripts/compile-proto
```

The python stubs are placed in a freshly created `./protos` folder.
This script use `pip` to install `grpcio-tools` and `protoc` compiler.



