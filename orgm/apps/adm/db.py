from sqlmodel import SQLModel, Field, create_engine, text
from typing import Optional, Dict
from dotenv import load_dotenv
import os
from rich import print
from sqlalchemy.dialects.postgresql import JSONB
from dataclasses import dataclass, field
import uuid

# Initialize these as None at the module level
DATABASE_USER = None
DATABASE_PASSWORD = None
DATABASE_HOST = None
DATABASE_NAME = None
DATABASE_SEARCH_PATH = None
DATABASE_URL = None
engine = None

def initialize_db():
    """Initialize database variables that were previously at module level"""
    global DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_NAME
    global DATABASE_SEARCH_PATH, DATABASE_URL, engine
    
    load_dotenv()
    
    DATABASE_USER = os.getenv("DATABASE_USER")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
    DATABASE_HOST = os.getenv("DATABASE_HOST")
    DATABASE_NAME = os.getenv("DATABASE_NAME")
    DATABASE_SEARCH_PATH = os.getenv("DATABASE_SEARCH_PATH")
    DATABASE_URL = (
        f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"
    )
    
    # Create the engine if needed
    if engine is None and all([DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_NAME]):
        try:
            if DATABASE_SEARCH_PATH:
                engine = create_engine(
                    DATABASE_URL,
                    connect_args={"options": f"-c search_path={DATABASE_SEARCH_PATH}"},
                )
            else:
                engine = create_engine(DATABASE_URL)
        except Exception as e:
            print(f"[bold red]Error al crear el motor de base de datos: {e}[/bold red]")


class Cliente(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(default="", max_length=255)
    nombre_comercial: str = Field(default="", max_length=255)
    numero: str = Field(default="", max_length=255)
    correo: str = Field(default="", max_length=255)
    direccion: str = Field(default="", max_length=255)
    ciudad: str = Field(default="", max_length=255)
    provincia: str = Field(default="", max_length=255)
    telefono: str = Field(default="", max_length=255)
    representante: str = Field(default="", max_length=255)
    telefono_representante: str = Field(default="", max_length=255)
    extension_representante: str = Field(default="", max_length=255)
    celular_representante: str = Field(default="", max_length=255)
    correo_representante: str = Field(default="", max_length=255)
    tipo_factura: str = Field(default="NCFC", max_length=255)
    fecha_actualizacion: str = Field(default="", max_length=255)
    logo_cliente: str = Field(default="/var/www/Logos/clientes", max_length=255)


class Proyecto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ubicacion: str = Field(default="", max_length=255)
    nombre_proyecto: str = Field(default="", max_length=255)
    descripcion: str = Field(default="")


class Ubicacion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    provincia: str = Field(default="", max_length=255)
    distrito: str = Field(default="", max_length=255)
    distritomunicipal: str = Field(default="", max_length=255)


class Categoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(default="", max_length=255)
    descripcion: str = Field(default="", max_length=255)


class Servicio(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(default="", max_length=255)
    descripcion: str = Field(default="", max_length=255)


class TipoFactura(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(default="", max_length=255)
    descripcion: str = Field(default="", max_length=255)


class PagoRecibido(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    id_cliente: Optional[int] = Field(default=None, foreign_key="cliente.id")
    moneda: str = Field(default="", max_length=50)
    monto: float = Field(default=0.0)
    fecha: str = Field(default="", max_length=255)
    comprobante: str = Field(default="", max_length=255)


class Cotizacion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    id_cliente: int = Field(foreign_key="cliente.id")
    id_proyecto: int = Field(foreign_key="proyecto.id")
    id_servicio: int = Field(foreign_key="servicio.id")
    moneda: str = Field(default="RD$", max_length=30)
    fecha: str = Field(default="", max_length=30)
    tasa_moneda: float = Field(default=0.0)
    tiempo_entrega: str = Field(default="3", max_length=30)
    avance: str = Field(default="60", max_length=30)
    validez: int = Field(default=30)
    estado: str = Field(default="GENERADA", max_length=30)
    idioma: str = Field(default="ES", max_length=30)
    descripcion: str = Field(default="")
    retencion: str = Field(default="NINGUNA", max_length=30)
    subtotal: float = Field(default=0.0)
    indirectos: float = Field(default=0.0)
    descuentop: float = Field(default=0.0)
    descuentom: float = Field(default=0.0)
    retencionp: float = Field(default=0.0)
    retencionm: float = Field(default=0.0)
    itbisp: float = Field(default=18.0)
    itbism: float = Field(default=0.0)
    total: float = Field(default=0.0)


class AsignacionPago(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    id_cotizacion: int = Field(foreign_key="cotizacion.id")
    id_pago: int = Field(foreign_key="pagorecibido.id")
    monto: float = Field(default=0.0)


class NCF(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    numero: str = Field(default="", max_length=20)
    fecha: str = Field(default="", max_length=20)


class NCFC(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    numero: str = Field(default="", max_length=20)
    fecha: str = Field(default="", max_length=20)


class NCG(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    numero: str = Field(default="", max_length=20)
    fecha: str = Field(default="", max_length=20)


class NCRE(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    numero: str = Field(default="", max_length=20)
    fecha: str = Field(default="", max_length=20)


class NDC(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    numero: str = Field(default="", max_length=20)
    fecha: str = Field(default="", max_length=20)


class NDD(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    numero: str = Field(default="", max_length=20)
    fecha: str = Field(default="", max_length=20)


class Unidad(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    unidad: str = Field(default="", max_length=20)
    descripcion: str = Field(default="", max_length=255)


class Material(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(default="", max_length=255)
    descripcion: Dict = Field(default={}, sa_type=JSONB)
    unidad: str = Field(default="", max_length=20)
    fecha: str = Field(default="", max_length=20)


class Servicios(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(default="")
    descripcion: Dict = Field(default={}, sa_type=JSONB)
    unidad: str = Field(default="", max_length=20)
    fecha: str = Field(default="", max_length=20)


class ManoDeObra(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(default="")
    descripcion: Dict = Field(default={}, sa_type=JSONB)
    unidad: str = Field(default="", max_length=20)
    fecha: str = Field(default="", max_length=20)


class Indirectos(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(default="")
    descripcion: Dict = Field(default={}, sa_type=JSONB)
    unidad: str = Field(default="", max_length=20)
    fecha: str = Field(default="", max_length=20)


class Herramientas(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(default="")
    descripcion: Dict = Field(default={}, sa_type=JSONB)
    unidad: str = Field(default="", max_length=20)
    fecha: str = Field(default="", max_length=20)


class Equipos(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(default="")
    descripcion: Dict = Field(default={}, sa_type=JSONB)
    unidad: str = Field(default="", max_length=20)
    fecha: str = Field(default="", max_length=20)


class Presupuesto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    id_cotizacion: int = Field(foreign_key="cotizacion.id")
    presupuesto: Dict = Field(default={}, sa_type=JSONB)


class Notas(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    id_cotizacion: int = Field(foreign_key="cotizacion.id")
    notas: Dict = Field(default={}, sa_type=JSONB)


class Factura(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    id_cotizacion: int = Field(foreign_key="cotizacion.id")
    id_cliente: int = Field(foreign_key="cliente.id")
    id_proyecto: int = Field(foreign_key="proyecto.id")
    moneda: str = Field(default="RD$", max_length=30)
    tipo_factura: str = Field(default="NCFC", max_length=30)
    fecha: str = Field(default="", max_length=30)
    tasa_moneda: float = Field(default=0.0)
    original: str = Field(default="VENDEDOR", max_length=30)
    estado: str = Field(default="GENERADA", max_length=30)
    idioma: str = Field(default="ES", max_length=30)
    comprobante: str = Field(default="", max_length=30)
    comprobante_valido: str = Field(default="", max_length=30)
    subtotal: float = Field(default=0.0)
    indirectos: float = Field(default=0.0)
    descuentop: float = Field(default=0.0)
    descuentom: float = Field(default=0.0)
    retencionp: float = Field(default=0.0)
    retencionm: float = Field(default=0.0)
    itbisp: float = Field(default=18.0)
    itbism: float = Field(default=0.0)
    total_sin_itbis: float = Field(default=0.0)
    total: float = Field(default=0.0)


@dataclass
class PartidaPresupuesto:
    id: str = None
    item: str = field(default="P-1")
    descripcion: str = field(default="Partida")
    cantidad: float = field(default=1)
    unidad: str = field(default="Ud.")
    moneda: str = field(default="RD$")
    precio: float = field(default=0.0)
    total: float = field(default=0.0)
    datos: list = field(default_factory=list)

    def __post_init__(self):
        if not self.id:
            self.id = self.generar_id()
        self.set_datos()

    def to_dict(self):
        return {
            "id": self.id,
            "item": self.item,
            "descripcion": self.descripcion,
            "cantidad": self.cantidad,
            "unidad": self.unidad,
            "moneda": self.moneda,
            "precio": self.precio,
            "total": self.total,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def get_total(self):
        self.total = round(self.cantidad * self.precio, 2)
        self.set_datos()
        return self.total

    @staticmethod
    def generar_id(n=6):
        return uuid.uuid4().hex[:n]

    def cambio_moneda(self, moneda: str = "RD$", tasa: float = 1):
        if self.precio > 0 and self.moneda != moneda and tasa != 1:
            self.precio = round(self.precio * tasa, 2)
            self.moneda = moneda
        self.set_datos()

    def set_datos(self):
        self.datos = []
        try:
            precio = "{:,.2f}".format(self.precio)
        except Exception as e:
            print(f"Error al formatear el precio: {e}")
            precio = self.precio
        try:
            total = "{:,.2f}".format(self.total)
        except Exception as e:
            print(f"Error al formatear el total: {e}")
            total = self.total
        self.datos.append(
            [
                self.item,
                self.descripcion,
                self.cantidad,
                self.unidad,
                self.moneda,
                precio,
                total,
            ]
        )

    def to_table(self):
        return self.datos


@dataclass
class CategoriaPresupuesto(PartidaPresupuesto):
    item: str = field(default="I-1")
    descripcion: str = field(default="Categoria")
    categoria: str = field(default="cat1")
    children: list = field(default_factory=list)

    def to_dict(self):
        data = super().to_dict()
        data["categoria"] = self.categoria
        data["children"] = [child.to_dict() for child in self.children]
        return data

    @classmethod
    def from_dict(cls, data):
        children_data = data.pop("children", [])
        children = []
        for child in children_data:
            if "children" in child:
                children.append(CategoriaPresupuesto.from_dict(child))
            else:
                children.append(PartidaPresupuesto.from_dict(child))
        return cls(children=children, **data)

    def get_total(self):
        if not self.children:
            self.total = round(self.cantidad * self.precio, 2)
            return self.total
        self.total = sum(child.get_total() for child in self.children)
        self.set_datos()
        return self.total

    def cambio_moneda(self, moneda: str = "RD$", tasa: float = 1):
        for child in self.children:
            child.cambio_moneda(moneda, tasa)
        self.set_datos()

    def to_table(self):
        """Recursively collects all data from parent and children into a list"""
        result = []
        # Add parent data
        if self.datos:
            result.extend(self.datos)

        # Recursively add children data
        for child in self.children:
            result.extend(child.to_table())

        return result


def create_db_schema():
    """Create database schema if needed"""
    if engine is None:
        initialize_db()
        
    if engine is None:
        print("[bold red]No se pudo crear el esquema: motor de base de datos no inicializado[/bold red]")
        return
        
    try:
        if DATABASE_SEARCH_PATH:
            with engine.connect() as c:
                c.execute(text(f"CREATE SCHEMA IF NOT EXISTS {DATABASE_SEARCH_PATH}"))
                c.commit()
                print(f"Esquema creado: {DATABASE_SEARCH_PATH}")
        SQLModel.metadata.create_all(engine)
        print("[bold green]Tablas creadas correctamente[/bold green]")
    except Exception as e:
        print(f"[bold red]Error al crear el esquema: {e}[/bold red]")


if __name__ == "__main__":
    create_db_schema()
    # with open("datos/template.csv", "r", encoding=
