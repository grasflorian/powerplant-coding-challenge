# How to run

```shell
uv sync
uv run serve
```

# Install uv

## Linux / MacOS

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Windows

```shell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Any system with pipx

```shell
pipx install uv
```

# Building the docker image

> [!NOTE] 
> You may need to run these commands with sudo

```shell
docker build -t powerplant-coding-challenge .
```

Then for running it

```shell
docker run -p 8888:8888 --user 999 powerplant-coding-challenge
```

# Running tests

```shell
pytest
```