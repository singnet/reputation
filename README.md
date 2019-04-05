# Reputation

This repository contains early pre-alpha proof-of-concept developments and experiments for Reputation system of SingularityNET.

At the moment, the work is in early stage.

Any source forks and contributions make sense only in case if are made in tight collaboration with SingularityNET.

Any production use and use other than for experimental purposes is not encouraged and can be done only at ones own risk.

## Contents

* Python [Reputation Agency Service wrapper](https://github.com/singnet/reputation/blob/master/reputation/aigents_reputation_api.py) based on [Aigents Java-based](https://github.com/aigents/aigents-java) reputation engine
* Python [Reputation Agency Service command line tool](https://github.com/singnet/reputation/blob/master/reputation/aigents_reputation_cli.py) based on [Aigents Java-based](https://github.com/aigents/aigents-java) reputation engine
* Python [native implementation of Reputation Agency Service](https://github.com/singnet/reputation/blob/master/reputation/reputation_service_api.py) 
* Python [simplistic simulation script](https://github.com/singnet/reputation/blob/master/reputation/reputation_scenario.py)
* Python [extended simulation framework](https://github.com/singnet/reputation-simulation)
* Auxiliary [scripts for SigluarityNET Adapter integration](https://github.com/singnet/reputation/tree/master/scripts)

## Development 

These instructions are intended to facilitate the development and testing of SingularityNET Reputation System. Users interested in deploying the reputation system should install the appropriate binary as [released](#release).

### Prerequisites

* Python/Pip
* Java 6 or later (needed for developments based on Aigents Java)
* Docker (Optional)

### Installing

* Clone the git repository

```bash
$ git clone git@github.com:singnet/reputation.git
$ cd reputation
```

In case there are problems with the script above, one can try a more stable http approach:

```bash
$ git clone https://github.com/singnet/reputation.git
$ cd reputation
```

* Install dependencies in editable/development mode on your local machine

```bash
$ bash scripts/install
```

### Aigents Server (required)

* Edit hosts file, adding the line with "127.0.0.1 localtest.com"

```
Mac: /private/etc/hosts
Linux: /etc/hosts
Windows: c:\WINDOWS\system32\drivers\etc\hosts 
```

### Testing

* Launch unit tests 

```bash
$ bash scripts/test
```


## Resources

For more information, see the following.

* [Reputation System Design for SingularityNET](https://blog.singularitynet.io/reputation-system-design-for-singularitynet-8b5b61e8ed0e)
* [A Reputation System for Artificial Societies](https://arxiv.org/abs/1806.07342) paper
* [Reputation System for Online Communities](https://arxiv.org/abs/1811.08149) paper (in Russian)
* [Reputation Consensus and System for Liquid Democracy Governance](https://www.youtube.com/watch?v=5Pi973JPbZA) video
