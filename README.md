## ORGM-CLI

Desarrollo de herramientas empresariales para personal avanzado de programacion, intelrigencia artificial, automatizacion de tareas. Las apis usadas son privadas, se deben desarrollar las propias y adaptar el codigo a la misma.

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

[bold green]
ORGM CLI: Herramienta integral de gestión y utilidades
[/bold green]

Administra clientes, proyectos, cotizaciones, Docker, variables de entorno y firma de documentos PDF. Automatiza tu flujo de trabajo desde la terminal.

Subcomandos principales:
client Gestión de clientes.
project Gestión de proyectos.
quotation Gestión de cotizaciones.
docker Gestión de imágenes Docker.
env Variables de entorno (.env).
pdf Operaciones con PDF (firmas).
ai Consulta al servicio de IA.
check Verifica URLs definidas en .env.
update Actualiza ORGM CLI.
install Instala ORGM CLI.
find-company Busca información de empresa por RNC.
currency-rate Obtiene tasa de cambio.

Para ayuda detallada:
orgm --help o orgm comando --help

[bold yellow]COMANDOS DE GESTIÓN DE CLIENTES[/bold yellow]
orgm client Menú interactivo de clientes.
orgm client list Lista todos los clientes.
orgm client show ID [--json] Muestra detalles de un cliente (opcionalmente en JSON).
orgm client find TÉRMINO Busca clientes.
orgm client create --nombre N --numero N ... Crea un nuevo cliente (ver --help para opciones).
orgm client edit ID --nombre N ... Modifica un cliente (ver --help para opciones).
orgm client delete ID [--confirmar] Elimina un cliente.
orgm client export ID [--clipboard] Exporta cliente a JSON (opcionalmente al portapapeles).

[bold yellow]COMANDOS DE GESTIÓN DE PROYECTOS[/bold yellow]
orgm project Menú interactivo de proyectos.
orgm project list Lista todos los proyectos.
orgm project show ID Muestra detalles de un proyecto.
orgm project find TÉRMINO Busca proyectos.
orgm project create Crea un nuevo proyecto (interactivo).
orgm project edit ID Modifica un proyecto (interactivo).
orgm project delete ID Elimina un proyecto.

[bold yellow]COMANDOS DE PDF[/bold yellow]
orgm pdf sign-file ARCHIVO_PDF ... Firma un PDF indicando ruta y coordenadas (ver --help).
orgm pdf sign Selector de archivos para firmar PDF (interactivo).

[bold yellow]COMANDOS DE COTIZACIONES[/bold yellow]
orgm quotation Menú interactivo de cotizaciones.
orgm quotation list Lista todas las cotizaciones.
orgm quotation show ID Muestra detalles de una cotización.
orgm quotation find TÉRMINO Busca cotizaciones (por cliente/proyecto).
orgm quotation create Crea una nueva cotización (interactivo).
orgm quotation edit ID Modifica una cotización (interactivo).
orgm quotation delete ID Elimina una cotización.

[bold yellow]COMANDOS DE IA[/bold yellow]
orgm ai prompt "PROMPT" [--config CONFIG] Genera texto con IA usando un prompt.
orgm ai configs Lista las configuraciones de IA disponibles.
orgm ai upload RUTA_ARCHIVO Sube un archivo de configuración de IA.
orgm ai create Crea una nueva configuración de IA (interactivo).
orgm ai edit NOMBRE_CONFIG Edita una configuración de IA existente (interactivo).

[bold yellow]COMANDOS DE DOCKER[/bold yellow]
orgm docker Menú interactivo de Docker.
orgm docker build Construye imagen Docker.
orgm docker build-nocache Construye imagen sin caché.
orgm docker save Guarda imagen en archivo tar.
orgm docker push Envía imagen al registry.
orgm docker tag Etiqueta imagen como latest.
orgm docker create-prod-context Crea contexto prod.
orgm docker deploy Despliega en contexto prod.
orgm docker remove-prod-context Elimina contexto prod.
orgm docker login Inicia sesión en Docker Hub.
