## ORGM-CLI

Desarrollo de herramientas empresariales para personal avanzado de programacion, intelrigencia artificial, automatizacion de tareas. Las apis usadas son privadas, se deben desarrollar las propias y adaptar el codigo a la misma.

### windows

```

powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv tool install "git+https://github.com/osmargm1202/cli.git"

```

### linux

```

wget -qO- https://astral.sh/uv/install.sh | sh
uv tool install "git+https://github.com/osmargm1202/cli.git"


uv tool install orgm

```

### upgrade

```

uv tool install orgm --upgrade


```
