# Reputation

This repository contains early pre-alpha proof-of-concept developments and experiments for Reputation system of SingularityNET.

At the moment, the work is in early stage.

Any source forks and contributions make sense only in case if are made in tight collaboration with SingularityNET.

Any production use and use other than for experimental purposes is not encouraged and can be done only at ones own risk.

## Contents

* Python [Reputation Agency Service wrapper](https://github.com/singnet/reputation/blob/master/agency/python/src/aigents_reputation_api.py) based on [Aigents Java-based](https://github.com/aigents/aigents-java) reputation engine
* Python [Reputation Agency Service command line tool](https://github.com/singnet/reputation/blob/master/agency/python/src/aigents_reputation_cli.py) based on [Aigents Java-based](https://github.com/aigents/aigents-java) reputation engine
* Python [native implementation of Reputation Agency Service](https://github.com/singnet/reputation/blob/master/agency/python/src/reputation_service_api.py) 
* Python [simplistic simulation script](https://github.com/singnet/reputation/blob/master/agency/python/src/reputation_scenario.py)
* Python [extended simulation framework](https://github.com/singnet/reputation/tree/master/agency/python/src/snsim)
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

#### Without Docker

* Edit hosts file, adding the line with "127.0.0.1 localtest.com"

```
Mac: /private/etc/hosts
Linux: /etc/hosts
Windows: c:\WINDOWS\system32\drivers\etc\hosts 
```

* Run Aigents Java Server

```
sh agency/python/src/aigents_server_start.sh 
```

* Install dependencies in editable/development mode on your local machine

```bash
$ bash scripts/install
```

#### With Docker

* Build the docker image if the first time 

```sh
$ bash scripts/docker-build
```

* Run into an interactive session (requires docker daemon running)

```bash
$ bash scripts/docker-run
```

If you run `pwd` the reuslt should be `/home/user/reputation`

* Run Aigents Java Server

```
sudo sh agency/python/src/aigents_server_start.sh 
```

* Install dependencies in editable/development mode on your local machine

```bash
$ sudo bash scripts/install
```


* In order to exit from the current Docker container

```bash
$ exit
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
