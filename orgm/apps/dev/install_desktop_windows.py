import os
from rich.console import Console
import subprocess

console = Console()

def crear_acceso_directo_windows():
    try:
        # Obtener ruta del escritorio
        ruta_escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
        
        # Crear acceso directo .lnk usando VBScript
        ruta_lnk = os.path.join(ruta_escritorio, "ORGM CLI.lnk")
        
        vbs_script = f'''
        Set oWS = WScript.CreateObject("WScript.Shell")
        Set oLink = oWS.CreateShortcut("{ruta_lnk}")
        oLink.TargetPath = "cmd.exe"
        oLink.Arguments = "/K orgm"
        oLink.WorkingDirectory = "{os.path.expanduser("~")}"
        oLink.Save
        '''
        
        # Guardar script temporal
        vbs_path = os.path.join(os.environ['TEMP'], 'create_shortcut.vbs')
        with open(vbs_path, 'w') as f:
            f.write(vbs_script)
            
        # Ejecutar script VBS
        subprocess.run(['cscript', '//Nologo', vbs_path], check=True)
        
        # Eliminar script temporal
        os.remove(vbs_path)

        console.print("✓ Acceso directo creado exitosamente", style="bold green")
        console.print(f"  Ubicación: {ruta_lnk}", style="dim")

    except Exception as e:
        console.print(f"✗ Error al crear el acceso directo: {str(e)}", style="bold red")

if __name__ == "__main__":
    crear_acceso_directo_windows()
