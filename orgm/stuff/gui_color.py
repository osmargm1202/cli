"""
Configuración de colores para interfaces gráficas de la aplicación.
"""

# Colores principales
FONDO_PRINCIPAL = "#121212"  # Gris oscuro casi negro
FONDO_SECUNDARIO = "#1E1E1E"  # Gris oscuro para contraste
FONDO_TARJETA = "#2D2D2D"  # Gris para tarjetas

# Colores de acentos
AZUL_PRIMARIO = "#2563EB"  # Azul para botones principales
AZUL_SECUNDARIO = "#3B82F6"  # Azul más claro para hover
ROJO_ERROR = "#EF4444"  # Rojo para botones de cancelar/errores
VERDE_EXITO = "#22C55E"  # Verde para acciones exitosas
AMARILLO_ADVERTENCIA = "#F59E0B"  # Amarillo para advertencias

# Colores de texto
TEXTO_PRINCIPAL = "#FFFFFF"  # Blanco para texto principal
TEXTO_SECUNDARIO = "#E5E5E5"  # Gris claro para texto secundario
TEXTO_DESHABILITADO = "#6B7280"  # Gris para texto deshabilitado

# Configuración de tema
TEMA_OSCURO = True  # Indicador de tema oscuro

# Clases Tailwind comunes
CLASE_BOTON_PRIMARIO = (
    "bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
)
CLASE_BOTON_CANCELAR = (
    "bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
)
CLASE_BOTON_EXITO = (
    "bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
)
CLASE_TARJETA = "bg-gray-800 rounded-lg shadow-lg p-4"
CLASE_INPUT = "bg-gray-700 text-white rounded px-3 py-2"
