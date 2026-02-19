@echo off
REM Script para ejecutar API Flask sin mostrar ventana CMD
REM Cambia al directorio de la API
cd /d "C:\Users\jirlesa\api-imprimir"

REM Ejecuta la API usando pythonw (sin ventana visible)
pythonw app.py

REM El script termina aquí - la API queda ejecutándose en segundo plano