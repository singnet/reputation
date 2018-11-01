# SingularityNet Escrow Adapter

## .proto definition

```proto
syntax = "proto3";

package adapter.snet.escrow;

message Reference {
  required string hash = 1;
  required int32 block = 2;
}

message Input {
  required string job_address  = 1;
}

message Output {
  required uint64 value = 1;
  required string consumer = 2;
  required string agent = 3;
  required string owner = 4;
  string state = 5;
  Reference deposit = 6;
  Reference withdraw = 7;
}
```

## Messages

### Reference

```
{ 
  hash: '0xb0c7f2753ce1533a1cbaffbad4ccdeb210ac579df71735d9de71047359e11a59',
  block: 15344 
}
```

### Input

```
{
  job_address: "0x988C8e2bc509b92960a79d4C92e6f139eEc165A4"
}
```

### Output

```
{ 
  value: 10000000,
  consumer: '0xabdd6525BC4012B07a3A3758070C676fAd70869B',
  agent: '0x2ED982c220feD6C9374e63804670fc16BD481b8f',
  owner: '0x5f1EB1F3FF1350C0A35e23013D0039a166c80B49',
  state: 'COMPLETED',
  deposit: 
   { hash: '0xb0c7f2753ce1533a1cbaffbad4ccdeb210ac579df71735d9de71047359e11a59',
     block: 1539356544 },
  withdraw: 
   { hash: '0x9a9d9db308fd0eaa3aeb6a0ae36feb34795c9019e1963d361ec2f49f1eb85184',
     block: 1539356568 }
}
```



