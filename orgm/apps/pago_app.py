import questionary
from rich.console import Console
from datetime import datetime
import typer
from orgm.apis.pago import registrar_pago, obtener_pagos, asignar_pago_a_cotizacion
from orgm.adm.clientes import obtener_clientes, obtener_cliente, buscar_clientes
from orgm.adm.cotizaciones import cotizaciones_por_cliente, obtener_cotizacion
from orgm.stuff.spinner import spinner

console = Console()

def pago_menu():
    """Menú interactivo para la gestión de pagos."""
    console.print("[bold blue]===== Gestión de Pagos =====[/bold blue]")
    
    opciones = [
        {"name": "📝 Registrar nuevo pago", "value": "registrar"},
        {"name": "📋 Listar pagos", "value": "listar"},
        {"name": "🔗 Asignar pago a cotización", "value": "asignar"},
        {"name": "🔍 Buscar pagos por cliente", "value": "buscar"},
        {"name": "⬅️ Volver al menú principal", "value": "volver"}
    ]
    
    try:
        seleccion = questionary.select(
            "Seleccione una opción:",
            choices=[opcion["name"] for opcion in opciones],
            use_indicator=True,
            use_shortcuts=True
        ).ask()
        
        if seleccion is None:  # Usuario presionó Ctrl+C
            return "exit"
            
        # Obtener el valor asociado a la selección
        accion = next(opcion["value"] for opcion in opciones if opcion["name"] == seleccion)
        
        if accion == "volver":
            return None  # Volver al menú principal
        elif accion == "registrar":
            return registrar_pago_interactivo()
        elif accion == "listar":
            return listar_pagos_interactivo()
        elif accion == "asignar":
            return asignar_pago_interactivo()
        elif accion == "buscar":
            return buscar_pagos_interactivo()
        else:
            console.print("[yellow]Opción no implementada[/yellow]")
            return pago_menu()  # Volver a mostrar el menú
    except Exception as e:
        console.print(f"[bold red]Error en el menú de pagos: {e}[/bold red]")
        return "error"


def seleccionar_cliente():
    """Función auxiliar para seleccionar un cliente."""
    # Preguntar cómo buscar el cliente
    metodo_busqueda = questionary.select(
        "¿Cómo desea seleccionar el cliente?",
        choices=[
            "Buscar por nombre o RNC",
            "Ver lista completa de clientes",
            "Ingresar ID manualmente",
            "Cancelar"
        ]
    ).ask()
    
    if metodo_busqueda == "Cancelar":
        return None
        
    if metodo_busqueda == "Ingresar ID manualmente":
        id_cliente_str = questionary.text("Ingrese el ID del cliente:").ask()
        try:
            id_cliente = int(id_cliente_str)
            # Verificar que el cliente existe
            with spinner(f"Verificando cliente ID {id_cliente}..."):
                cliente = obtener_cliente(id_cliente)
            
            if cliente:
                return id_cliente
            else:
                console.print(f"[bold red]No se encontró un cliente con ID {id_cliente}[/bold red]")
                return seleccionar_cliente()
        except ValueError:
            console.print("[bold red]El ID debe ser un número entero[/bold red]")
            return seleccionar_cliente()
    
    elif metodo_busqueda == "Buscar por nombre o RNC":
        termino = questionary.text("Ingrese término de búsqueda:").ask()
        if not termino:
            console.print("[yellow]Búsqueda cancelada[/yellow]")
            return seleccionar_cliente()
            
        with spinner(f"Buscando clientes con '{termino}'..."):
            clientes = buscar_clientes(termino)
        
        if not clientes:
            console.print("[yellow]No se encontraron clientes con ese criterio.[/yellow]")
            return seleccionar_cliente()
    else:  # Ver lista completa
        with spinner("Obteniendo lista de clientes..."):
            clientes = obtener_clientes()
        
        if not clientes:
            console.print("[yellow]No hay clientes registrados.[/yellow]")
            return seleccionar_cliente()
    
    # Crear lista de opciones para selección
    opciones = []
    for cliente in clientes:
        # Usar getattr en lugar de get para acceder a los atributos de los objetos Cliente
        nombre = getattr(cliente, "nombre", "Sin nombre")
        id_cliente = getattr(cliente, "id", "N/A")
        ruc = getattr(cliente, "numero", "Sin RUC/RNC")
        opciones.append({
            "name": f"ID: {id_cliente} - {nombre} ({ruc})",
            "value": id_cliente
        })
    
    opciones.append({"name": "⬅️ Volver", "value": "volver"})
    
    # Mostrar opciones para selección
    seleccion = questionary.select(
        "Seleccione un cliente:",
        choices=[opcion["name"] for opcion in opciones],
        use_indicator=True
    ).ask()
    
    if seleccion is None or seleccion == "⬅️ Volver":
        return seleccionar_cliente()
        
    # Obtener el ID del cliente seleccionado
    id_cliente = next(opcion["value"] for opcion in opciones if opcion["name"] == seleccion)
    return id_cliente


def registrar_pago_interactivo():
    """Interfaz interactiva para registrar un nuevo pago."""
    console.print("[bold blue]===== Registrar Nuevo Pago =====[/bold blue]")
    
    # Seleccionar cliente
    id_cliente = seleccionar_cliente()
    if id_cliente is None:
        console.print("[yellow]Operación cancelada[/yellow]")
        return pago_menu()
    
    # Obtener datos del cliente para mostrar
    with spinner(f"Cargando datos del cliente {id_cliente}..."):
        cliente = obtener_cliente(id_cliente)
    
    # Usar getattr en lugar de get
    console.print(f"Cliente seleccionado: [bold]{getattr(cliente, 'nombre', 'Desconocido')}[/bold] (ID: {id_cliente})")
    
    # Solicitar datos del pago
    monto_str = questionary.text("Monto del pago:").ask()
    try:
        monto = float(monto_str)
    except ValueError:
        console.print("[bold red]El monto debe ser un número[/bold red]")
        return registrar_pago_interactivo()
    
    moneda = questionary.select(
        "Moneda:",
        choices=["DOP", "USD", "EUR"],
        default="DOP"
    ).ask()
    
    fecha_default = datetime.now().strftime("%Y-%m-%d")
    fecha = questionary.text(f"Fecha (YYYY-MM-DD):", default=fecha_default).ask()
    
    comprobante = questionary.text("Número de comprobante (opcional):").ask()
    
    # Confirmar datos
    console.print("\n[bold]Datos del pago:[/bold]")
    # Usar getattr en lugar de get
    console.print(f"Cliente: {getattr(cliente, 'nombre', 'Desconocido')} (ID: {id_cliente})")
    console.print(f"Monto: {monto} {moneda}")
    console.print(f"Fecha: {fecha}")
    if comprobante:
        console.print(f"Comprobante: {comprobante}")
    
    confirmar = questionary.confirm("¿Confirma el registro del pago?").ask()
    if not confirmar:
        console.print("[yellow]Operación cancelada[/yellow]")
        return pago_menu()
    
    # Registrar el pago
    with spinner("Registrando pago..."):
        resultado = registrar_pago(id_cliente, moneda, monto, fecha, comprobante)
    
    if resultado:
        # Aquí resultado es un diccionario, podemos usar get
        console.print(f"[bold green]✓ Pago registrado correctamente con ID {resultado.get('id')}[/bold green]")
        
        # Preguntar si desea asignar el pago a alguna cotización
        asignar = questionary.confirm("¿Desea asignar este pago a una cotización?").ask()
        if asignar:
            # Obtener cotizaciones del cliente
            with spinner(f"Obteniendo cotizaciones del cliente {id_cliente}..."):
                cotizaciones = cotizaciones_por_cliente(id_cliente)
            
            if not cotizaciones:
                console.print("[yellow]El cliente no tiene cotizaciones disponibles para asignar el pago.[/yellow]")
                input("\nPresione Enter para continuar...")
                return pago_menu()
            
            # Preparar lista de opciones
            opciones = []
            for cot in cotizaciones:
                opciones.append({
                    "name": f"ID: {cot.get('id')} - {cot.get('descripcion', 'Sin descripción')[:30]}... - Total: {cot.get('total')} {cot.get('moneda', 'DOP')}",
                    "value": str(cot.get('id'))
                })
            
            # Preguntar al usuario qué cotización
            seleccion = questionary.select(
                "Seleccione la cotización a la que desea asignar el pago:",
                choices=[opcion["name"] for opcion in opciones] + ["Cancelar"]
            ).ask()
            
            if seleccion == "Cancelar":
                console.print("[yellow]Asignación cancelada[/yellow]")
                input("\nPresione Enter para continuar...")
                return pago_menu()
            
            # Obtener el ID de la cotización seleccionada
            id_cot = next(opcion["value"] for opcion in opciones if opcion["name"] == seleccion)
            
            # Preguntar monto a asignar (por defecto todo)
            monto_asignar_str = questionary.text(
                f"Monto a asignar a la cotización ID {id_cot}:", 
                default=str(monto)
            ).ask()
            
            try:
                monto_asignar = float(monto_asignar_str)
            except ValueError:
                console.print("[bold red]El monto debe ser un número[/bold red]")
                monto_asignar = monto
            
            # Asignar el pago
            with spinner("Asignando pago..."):
                asignacion = asignar_pago_a_cotizacion(resultado.get('id'), int(id_cot), monto_asignar)
            
            if asignacion:
                console.print(f"[bold green]✓ Pago asignado correctamente a la cotización ID {id_cot}[/bold green]")
            else:
                console.print("[bold red]✗ Error al asignar el pago[/bold red]")
    else:
        console.print("[bold red]✗ Error al registrar el pago[/bold red]")
    
    input("\nPresione Enter para continuar...")
    return pago_menu()


def listar_pagos_interactivo():
    """Interfaz interactiva para listar pagos."""
    console.print("[bold blue]===== Listar Pagos =====[/bold blue]")
    
    filtrar = questionary.confirm("¿Desea filtrar por cliente?").ask()
    id_cliente = None
    
    if filtrar:
        id_cliente = seleccionar_cliente()
        if id_cliente is None:
            console.print("[yellow]Filtrado cancelado, mostrando todos los pagos[/yellow]")
    
    # Obtener y mostrar pagos
    with spinner("Obteniendo pagos..."):
        pagos = obtener_pagos(id_cliente)
    
    if not pagos:
        console.print("[yellow]No se encontraron pagos.[/yellow]")
        input("\nPresione Enter para continuar...")
        return pago_menu()
    
    # Crear tabla para mostrar resultados
    from rich.table import Table
    tabla = Table(title="Pagos Registrados", show_header=True, header_style="bold magenta")
    tabla.add_column("ID", style="dim")
    tabla.add_column("Cliente")
    tabla.add_column("Monto", justify="right")
    tabla.add_column("Moneda")
    tabla.add_column("Fecha")
    tabla.add_column("Comprobante")
    
    # Obtener información de clientes y crear un diccionario de id:nombre
    clientes_dict = {}
    with spinner("Cargando información de clientes..."):
        clientes_lista = obtener_clientes()
        for c in clientes_lista:
            # Usar getattr en lugar de get ya que c es un objeto Cliente
            clientes_dict[getattr(c, 'id', 0)] = getattr(c, 'nombre', f"Cliente {getattr(c, 'id', 'N/A')}")
    
    for pago in pagos:
        # pago es un diccionario, podemos usar get
        id_cliente_pago = pago.get("id_cliente")
        # Buscar el nombre del cliente en nuestro diccionario
        nombre_cliente = clientes_dict.get(id_cliente_pago, f"Cliente {id_cliente_pago}")
        
        tabla.add_row(
            str(pago.get("id", "N/A")),
            nombre_cliente,
            f"{pago.get('monto', 0):,.2f}",
            pago.get("moneda", "DOP"),
            pago.get("fecha", "N/A"),
            pago.get("comprobante", "")
        )
    
    console.print(tabla)
    input("\nPresione Enter para continuar...")
    return pago_menu()


def buscar_pagos_interactivo():
    """Interfaz interactiva para buscar pagos por cliente."""
    console.print("[bold blue]===== Buscar Pagos por Cliente =====[/bold blue]")
    
    # Preguntar si desea filtrar por cliente
    filtrar_cliente = questionary.confirm("¿Desea filtrar por cliente?").ask()
    
    id_cliente = None
    cliente = None
    
    if filtrar_cliente:
        id_cliente = seleccionar_cliente()
        if id_cliente is None:
            console.print("[yellow]Búsqueda cancelada[/yellow]")
            return pago_menu()
        
        # Obtener datos del cliente para mostrar
        with spinner(f"Cargando datos del cliente {id_cliente}..."):
            cliente = obtener_cliente(id_cliente)
        
        # Usar getattr en lugar de get
        console.print(f"Cliente seleccionado: [bold]{getattr(cliente, 'nombre', 'Desconocido')}[/bold] (ID: {id_cliente})")
    
    # Obtener pagos
    with spinner("Buscando pagos..."):
        pagos = obtener_pagos(id_cliente)
    
    if not pagos:
        mensaje = "No se encontraron pagos"
        if id_cliente:
            mensaje += f" para el cliente {getattr(cliente, 'nombre', 'ID: ' + str(id_cliente))}"
        console.print(f"[yellow]{mensaje}[/yellow]")
        return pago_menu()
    
    # Mostrar tabla de pagos
    from rich.table import Table
    
    tabla = Table(title="Pagos encontrados")
    tabla.add_column("ID", justify="right", style="cyan")
    tabla.add_column("Cliente", style="green")
    tabla.add_column("Monto", justify="right", style="yellow")
    tabla.add_column("Moneda", style="magenta")
    tabla.add_column("Fecha", style="blue")
    tabla.add_column("Comprobante", style="dim")
    tabla.add_column("Estado", style="bold")
    
    for pago in pagos:
        # Aquí pago es un diccionario, usamos get
        id_pago = pago.get("id", "N/A")
        
        # Si no tenemos nombre de cliente, lo buscamos
        nombre_cliente = pago.get("nombre_cliente", "")
        if not nombre_cliente and "id_cliente" in pago:
            cliente_id = pago.get("id_cliente")
            cliente_obj = obtener_cliente(cliente_id)
            if cliente_obj:
                nombre_cliente = getattr(cliente_obj, "nombre", f"ID: {cliente_id}")
        
        monto = pago.get("monto", 0)
        moneda = pago.get("moneda", "")
        fecha = pago.get("fecha", "")
        comprobante = pago.get("comprobante", "")
        
        # Verificar si está asignado a cotización
        estado = "Sin asignar"
        if pago.get("id_cotizacion"):
            estado = f"Asignado a Cotización #{pago.get('id_cotizacion')}"
        
        tabla.add_row(
            str(id_pago),
            nombre_cliente,
            f"{monto:,.2f}",
            moneda,
            fecha,
            comprobante,
            estado
        )
    
    console.print(tabla)
    
    # Preguntar si desea asignar algún pago
    asignar = questionary.confirm("¿Desea asignar alguno de estos pagos a una cotización?").ask()
    if asignar:
        return asignar_pago_interactivo()
    
    return pago_menu()


def asignar_pago_interactivo():
    """Interfaz interactiva para asignar un pago a una cotización."""
    console.print("[bold blue]===== Asignar Pago a Cotización =====[/bold blue]")
    
    # Primero seleccionar un cliente
    id_cliente = seleccionar_cliente()
    if id_cliente is None:
        console.print("[yellow]Operación cancelada[/yellow]")
        return pago_menu()
    
    # Obtener datos del cliente para mostrar
    with spinner(f"Cargando datos del cliente {id_cliente}..."):
        cliente = obtener_cliente(id_cliente)
    
    # Usar getattr en lugar de get
    console.print(f"Cliente seleccionado: [bold]{getattr(cliente, 'nombre', 'Desconocido')}[/bold] (ID: {id_cliente})")
    
    # Obtener pagos sin asignar del cliente
    with spinner(f"Obteniendo pagos sin asignar del cliente {id_cliente}..."):
        pagos = obtener_pagos(id_cliente, solo_sin_asignar=True)
    
    if not pagos:
        console.print("[yellow]El cliente no tiene pagos disponibles para asignar.[/yellow]")
        return pago_menu()
    
    # Crear opciones para seleccionar el pago
    opciones_pago = []
    for pago in pagos:
        id_pago = pago.get("id", "N/A")
        monto = pago.get("monto", 0)
        moneda = pago.get("moneda", "")
        fecha = pago.get("fecha", "")
        comprobante = pago.get("comprobante", "") or "Sin comprobante"
        
        opciones_pago.append({
            "name": f"ID: {id_pago} - {monto:,.2f} {moneda} - {fecha} - {comprobante}",
            "value": id_pago
        })
    
    opciones_pago.append({"name": "⬅️ Cancelar", "value": "cancelar"})
    
    # Seleccionar pago
    seleccion_pago = questionary.select(
        "Seleccione el pago a asignar:",
        choices=[opcion["name"] for opcion in opciones_pago],
        use_indicator=True
    ).ask()
    
    if seleccion_pago is None or seleccion_pago == "⬅️ Cancelar":
        console.print("[yellow]Operación cancelada[/yellow]")
        return pago_menu()
    
    # Obtener el ID del pago seleccionado
    id_pago = next(opcion["value"] for opcion in opciones_pago if opcion["name"] == seleccion_pago)
    
    # Obtener cotizaciones del cliente
    with spinner(f"Obteniendo cotizaciones del cliente {id_cliente}..."):
        cotizaciones = cotizaciones_por_cliente(id_cliente)
    
    if not cotizaciones:
        console.print("[yellow]El cliente no tiene cotizaciones disponibles para asignar el pago.[/yellow]")
        return pago_menu()
    
    # Crear opciones para seleccionar la cotización
    opciones_cotizacion = []
    for cotizacion in cotizaciones:
        id_cotizacion = cotizacion.get("id", "N/A")
        descripcion = cotizacion.get("descripcion", "Sin descripción")
        monto = cotizacion.get("monto_total", 0)
        moneda = cotizacion.get("moneda", "")
        fecha = cotizacion.get("fecha", "")
        
        # Obtener el monto ya pagado
        monto_pagado = sum(p.get("monto", 0) for p in obtener_pagos(id_cliente=id_cliente, id_cotizacion=id_cotizacion))
        
        opciones_cotizacion.append({
            "name": f"ID: {id_cotizacion} - {descripcion} - {monto:,.2f} {moneda} - {fecha} - Pagado: {monto_pagado:,.2f} {moneda}",
            "value": id_cotizacion
        })
    
    opciones_cotizacion.append({"name": "⬅️ Cancelar", "value": "cancelar"})
    
    # Seleccionar cotización
    seleccion_cotizacion = questionary.select(
        "Seleccione la cotización a la que asignar el pago:",
        choices=[opcion["name"] for opcion in opciones_cotizacion],
        use_indicator=True
    ).ask()
    
    if seleccion_cotizacion is None or seleccion_cotizacion == "⬅️ Cancelar":
        console.print("[yellow]Operación cancelada[/yellow]")
        return pago_menu()
    
    # Obtener el ID de la cotización seleccionada
    id_cotizacion = next(opcion["value"] for opcion in opciones_cotizacion if opcion["name"] == seleccion_cotizacion)
    
    # Confirmar la asignación
    console.print("\n[bold]Datos de la asignación:[/bold]")
    console.print(f"Cliente: {getattr(cliente, 'nombre', 'Desconocido')} (ID: {id_cliente})")
    console.print(f"Pago ID: {id_pago}")
    console.print(f"Cotización ID: {id_cotizacion}")
    
    confirmar = questionary.confirm("¿Confirma la asignación del pago a esta cotización?").ask()
    if not confirmar:
        console.print("[yellow]Operación cancelada[/yellow]")
        return pago_menu()
    
    # Asignar el pago
    with spinner("Asignando pago..."):
        resultado = asignar_pago_a_cotizacion(id_pago, id_cotizacion)
    
    if resultado:
        console.print(f"[bold green]✓ Pago asignado correctamente a la cotización #{id_cotizacion}[/bold green]")
    else:
        console.print("[bold red]Error al asignar el pago[/bold red]")
    
    return pago_menu() 