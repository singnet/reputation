## Docker instructions

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
sudo sh reputation/aigents_server_start.sh 
```

* Install dependencies in editable/development mode on your local machine

```bash
$ sudo bash scripts/install
```


* In order to exit from the current Docker container

```bash
$ exit
```
