[bold green]
ORGM CLI: Herramienta integral de gestión y utilidades
[/bold green]

Administra clientes, proyectos, cotizaciones, Docker, variables de entorno y firma de documentos PDF. Automatiza tu flujo de trabajo desde la terminal.

Subcomandos principales:
[blue]client[/blue] Gestión de clientes.
[blue]project[/blue] Gestión de proyectos.
[blue]quotation[/blue] Gestión de cotizaciones.
[blue]docker[/blue] Gestión de imágenes Docker.
[blue]env[/blue] Variables de entorno (.env).
[blue]pdf[/blue] Operaciones con PDF (firmas).
[blue]ai[/blue] Consulta al servicio de IA.
[blue]check[/blue] Verifica URLs definidas en .env.
[blue]update[/blue] Actualiza ORGM CLI.
[blue]install[/blue] Instala ORGM CLI.
[blue]find-company[/blue] Busca información de empresa por RNC.
[blue]currency-rate[/blue] Obtiene tasa de cambio.

Para ayuda detallada:
[blue]orgm --help[/blue] o [blue]orgm [red]comando[/red] --help[/blue]

[bold yellow]COMANDOS DE GESTIÓN DE CLIENTES[/bold yellow]
[blue]orgm client[/blue] Menú interactivo de clientes.
[blue]orgm client list[/blue] Lista todos los clientes.
[blue]orgm client show [red]ID[/red] [--json][/blue] Muestra detalles de un cliente (opcionalmente en JSON).
[blue]orgm client find [red]TÉRMINO[/red][/blue] Busca clientes.
[blue]orgm client create --nombre [red]N[/red] --numero [red]N[/red] ...[/blue] Crea un nuevo cliente (ver --help para opciones).
[blue]orgm client edit [red]ID[/red] --nombre [red]N[/red] ...[/blue] Modifica un cliente (ver --help para opciones).
[blue]orgm client delete [red]ID[/red] [--confirmar][/blue] Elimina un cliente.
[blue]orgm client export [red]ID[/red] [--clipboard][/blue] Exporta cliente a JSON (opcionalmente al portapapeles).

[bold yellow]COMANDOS DE GESTIÓN DE PROYECTOS[/bold yellow]
[blue]orgm project[/blue] Menú interactivo de proyectos.
[blue]orgm project list[/blue] Lista todos los proyectos.
[blue]orgm project show [red]ID[/red][/blue] Muestra detalles de un proyecto.
[blue]orgm project find [red]TÉRMINO[/red][/blue] Busca proyectos.
[blue]orgm project create[/blue] Crea un nuevo proyecto (interactivo).
[blue]orgm project edit [red]ID[/red][/blue] Modifica un proyecto (interactivo).
[blue]orgm project delete [red]ID[/red][/blue] Elimina un proyecto.

[bold yellow]COMANDOS DE PDF[/bold yellow]
[blue]orgm pdf sign-file [red]ARCHIVO_PDF[/red] ...[/blue] Firma un PDF indicando ruta y coordenadas (ver --help).
[blue]orgm pdf sign[/blue] Selector de archivos para firmar PDF (interactivo).

[bold yellow]COMANDOS DE COTIZACIONES[/bold yellow]
[blue]orgm quotation[/blue] Menú interactivo de cotizaciones.
[blue]orgm quotation list[/blue] Lista todas las cotizaciones.
[blue]orgm quotation show [red]ID[/red][/blue] Muestra detalles de una cotización.
[blue]orgm quotation find [red]TÉRMINO[/red][/blue] Busca cotizaciones (por cliente/proyecto).
[blue]orgm quotation create[/blue] Crea una nueva cotización (interactivo).
[blue]orgm quotation edit [red]ID[/red][/blue] Modifica una cotización (interactivo).
[blue]orgm quotation delete [red]ID[/red][/blue] Elimina una cotización.

[bold yellow]COMANDOS DE IA[/bold yellow]
[blue]orgm ai prompt "PROMPT" [--config CONFIG][/blue] Genera texto con IA usando un prompt.
[blue]orgm ai configs[/blue] Lista las configuraciones de IA disponibles.
[blue]orgm ai upload [red]RUTA_ARCHIVO[/red][/blue] Sube un archivo de configuración de IA.
[blue]orgm ai create[/blue] Crea una nueva configuración de IA (interactivo).
[blue]orgm ai edit [red]NOMBRE_CONFIG[/red][/blue] Edita una configuración de IA existente (interactivo).

[bold yellow]COMANDOS DE DOCKER[/bold yellow]
[blue]orgm docker[/blue] Menú interactivo de Docker.
[blue]orgm docker build[/blue] Construye imagen Docker.
[blue]orgm docker build-nocache[/blue] Construye imagen sin caché.
[blue]orgm docker save[/blue] Guarda imagen en archivo tar.
[blue]orgm docker push[/blue] Envía imagen al registry.
[blue]orgm docker tag[/blue] Etiqueta imagen como latest.
[blue]orgm docker create-prod-context[/blue] Crea contexto prod.
[blue]orgm docker deploy[/blue] Despliega en contexto prod.
[blue]orgm docker remove-prod-context[/blue] Elimina contexto prod.
[blue]orgm docker login[/blue] Inicia sesión en Docker Hub.
