[bold green]
ORGM CLI: Herramienta integral de gestión y utilidades
[/bold green]

Administra clientes, proyectos, variables de entorno y firma de documentos PDF. Automatiza tu flujo de trabajo desde la terminal.

Algunos comandos principales:
[blue]cliente[/blue] Gestión de clientes.
[blue]proyecto[/blue] Gestión de proyectos.
[blue]env[/blue] Variables de entorno (.env).
[blue]pdf[/blue] Operaciones con PDF (firmas).
[blue]update[/blue] Actualiza ORGM CLI.
[blue]install[/blue] Instala ORGM CLI.
[blue]cotizacion[/blue] Gestión de cotizaciones.
[blue]ai[/blue] Consulta al servicio de IA.
[blue]docker[/blue] Gestión de imágenes Docker.

Para ayuda detallada:
[blue]orgm --help[/blue] o [blue]orgm [red]comando[/red] --help[/blue]

[bold yellow]COMANDOS DE GESTIÓN DE CLIENTES[/bold yellow]
[blue]orgm cliente[/blue] Menú interactivo de clientes.
[blue]orgm cliente listar[/blue] Lista todos los clientes.
[blue]orgm cliente buscar [red]TÉRMINO[/red][/blue] Busca clientes.
[blue]orgm cliente crear[/blue] Crea un nuevo cliente.
[blue]orgm cliente modificar [red]ID[/red][/blue] Modifica un cliente.
[blue]orgm cliente eliminar [red]ID[/red][/blue] Elimina un cliente.

[bold yellow]COMANDOS DE GESTIÓN DE PROYECTOS[/bold yellow]
[blue]orgm proyecto[/blue] Menú interactivo de proyectos.
[blue]orgm proyecto listar[/blue] Lista todos los proyectos.
[blue]orgm proyecto buscar [red]TÉRMINO[/red][/blue] Busca proyectos.
[blue]orgm proyecto crear[/blue] Crea un nuevo proyecto.
[blue]orgm proyecto modificar [red]ID[/red][/blue] Modifica un proyecto.
[blue]orgm proyecto eliminar [red]ID[/red][/blue] Elimina un proyecto.

[bold yellow]COMANDOS DE PDF[/bold yellow]
[blue]orgm pdf firmar-ruta-archivo [red]ARCHIVO_PDF[/red] --x [red]X[/red] --y [red]Y[/red] --ancho [red]ANCHO[/red] [--salida ARCHIVO][/blue] Firma un PDF indicando ruta.
[blue]orgm pdf firmar [--x X] [--y Y] [--ancho ANCHO][/blue] Selector de archivos para firmar PDF.

[bold yellow]COMANDOS DE COTIZACIONES[/bold yellow]
[blue]orgm cotizacion[/blue] Menú interactivo de cotizaciones.
[blue]orgm cotizacion listar[/blue] Lista todas las cotizaciones.
[blue]orgm cotizacion buscar [red]TÉRMINO[/red][/blue] Busca cotizaciones.
[blue]orgm cotizacion crear[/blue] Crea una nueva cotización.
[blue]orgm cotizacion modificar [red]ID[/red][/blue] Modifica una cotización.
[blue]orgm cotizacion eliminar [red]ID[/red][/blue] Elimina una cotización.

[bold yellow]COMANDOS DE IA[/bold yellow]
[blue]orgm ai [--config CONFIG] "PROMPT"[/blue] Genera texto con IA.

[bold yellow]COMANDOS DE DOCKER[/bold yellow]
[blue]orgm docker[/blue] Menú interactivo de Docker.
[blue]orgm docker build[/blue] Construye imagen Docker.
[blue]orgm docker build_no_cache[/blue] Construye imagen sin caché.
[blue]orgm docker save[/blue] Guarda imagen en archivo tar.
[blue]orgm docker push[/blue] Envía imagen al registry.
[blue]orgm docker tag[/blue] Etiqueta imagen como latest.
[blue]orgm docker create_prod_context[/blue] Crea contexto prod.
[blue]orgm docker deploy[/blue] Despliega en contexto prod.
[blue]orgm docker remove_prod_context[/blue] Elimina contexto prod.
[blue]orgm docker login[/blue] Inicia sesión en Docker Hub.
