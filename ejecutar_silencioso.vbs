Set objShell = CreateObject("WScript.Shell")

' Cambia al directorio de la API y ejecuta con pythonw (sin ventana visible)
objShell.Run "cmd /c cd /d ""C:\Users\jirlesa\api-imprimir"" && pythonw app.py", 0, False

' El script termina aquí - la API queda ejecutándose en segundo plano