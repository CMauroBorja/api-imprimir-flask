Set objShell = CreateObject("WScript.Shell")

objShell.Run "cmd /c cd /d """ & CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & """ && pythonw run.py", 0, False