# Dynamic Airflow

## Running project

```bash
docker compose up --build airflow-init
docker compose up -d
```

## Formatting

We use [yapf](https://github.com/google/yapf) to format the code. To format the code, first install the formatting requirements.

### VSCode extension

Install [yapf](https://marketplace.visualstudio.com/items?itemName=eeyore.yapf)

### Auto format code at git commit

```bash
pip3 install -e '.[formatting]'

# Install the git hook scripts
pre-commit install
```

(optional) Run against all the files:

```bash
pre-commit run --all-files
```
