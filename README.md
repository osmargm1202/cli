### windows

```

powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv tool install "git+https://github.com/osmargm1202/cli.git"

```

### linux

```

curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install "git+https://github.com/osmargm1202/cli.git"

```

### linux

```

wget -qO- https://astral.sh/uv/install.sh | sh
uv tool install "git+https://github.com/osmargm1202/cli.git"

```

```
uv pip install --upgrade pip
uv pip install --upgrade build
uv pip install --upgrade twine
uv run build
uv run twine upload dist/*

```