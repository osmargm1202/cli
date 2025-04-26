@echo off

REM Actualizar el paquete de ORGM CLI en Windows
ECHO Actualizando paquete de ORGM CLI

REM Obtener la rama desde la variable de entorno GIT_BRANCH o usar master por defecto
IF "%GIT_BRANCH%"=="" (
    SET "branch=master"
) ELSE (
    SET "branch=%GIT_BRANCH%"
)

REM Construir la URL del repositorio
SET "giturl=%GIT_URL%@%branch%"

REM Desinstalar la versión actual
ECHO Desinstalando versión actual...
uv tool uninstall orgm
IF ERRORLEVEL 1 GOTO Error

REM Instalar la nueva versión desde la rama especificada
ECHO Instalando nueva versión desde la rama %branch%...
uv tool install --force git+%giturl%
IF ERRORLEVEL 1 GOTO Error

ECHO Paquete instalado correctamente desde la rama %branch%.
GOTO End

:Error
ECHO Error al actualizar el paquete.
EXIT /B 1

:End
EXIT /B 0 