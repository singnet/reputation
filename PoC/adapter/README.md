# Adapater

The `class` Adapater can be extended and provides developers to write their own adapters for reputation purpose.

To be initialized, you need to pass  the `.proto` file containing the definition for input and output loaded in-memory and passed to the constructor:


```js 
const protoFile = fs.readFileSync('./path/to/file.proto');
const adapter   = new Adapter({ proto : protoFile });
```


You can access to the ProtocolBuffer `messages` property and the methods `encode` and `decode`

```js
const InputBuffer = adapter.encode(jsonSchema);
const jsonSchema  = adapter.decode(InputBuffer);
```

# Custom adapter

You can find here an [example](https://github.com/singnet/reputation/tree/master/PoC/adapter/snet/escrow)
