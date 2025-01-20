# GenshinImpact

## Install
```bash
conda create -n crawler python=3.12.0
conda activate crawler

# install poetry
curl -sSL https://install.python-poetry.org | python3 -
poetry install
```

## Development
```bash
# install the environment
make install

# configure pre-commit
pre-commit install --config dev_config/python/.pre-commit-config.yaml

# install playwright
pip install playwright
playwright install

# install elastic search
brew install openjdk # install java
sudo ./bin/elasticsearch # start elastic search
```
