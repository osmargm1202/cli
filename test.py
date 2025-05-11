from nextcloud_client import Client

nc = Client('https://tunextcloud.example.com')
nc.login('usuario', 'tu_contraseña')

# Listar contenido de la raíz
print(nc.list())

# Crear directorio
nc.mkdir('/nueva_carpeta')

# Subir archivo
nc.put_file('/nueva_carpeta/mi_archivo.txt', 'mi_archivo.txt')

print("Contenido de /nueva_carpeta:", nc.list('/nueva_carpeta'))