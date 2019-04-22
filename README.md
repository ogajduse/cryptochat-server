# cryptochat-server

Server side for Cryptochat.

## Installation

### Docker

```bash
docker pull ogajduse/cryptochat-server
```

### Manually

Clone this repository:

```bash
git clone https://github.com/ogajduse/cryptochat-server.git && cd cryptochat-server
```

Install pipenv:

**Debian**

```bash
pip install pipenv
```

**Fedora**

```bash
dnf -y install pipenv
```

Install required python packages:

```
pipenv --three install
```

## Run the server

### Docker

```
docker run -p 8888:8888 -ti cryptochat-server
```

### Manually

```
mkdir -p .data
echo DATABASE_LOCATION=$PWD/.data >> .env
```

Run the server:

```
pipenv run python app.py
```

## Check

```
curl localhost:8888
```




