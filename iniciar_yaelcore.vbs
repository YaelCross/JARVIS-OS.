' Inicia YAELCORE-OS en segundo plano (sin ventana de consola).
' Lo usa el inicio automatico de Windows, pero tambien puedes
' darle doble clic para abrir el sistema.

Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

carpeta = fso.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = carpeta

python = carpeta & "\.venv\Scripts\pythonw.exe"

If Not fso.FileExists(python) Then
    MsgBox "No se encontro el entorno virtual:" & vbCrLf & python & vbCrLf & vbCrLf & _
        "Crea el entorno .venv e instala las dependencias antes de iniciar YAELCORE-OS.", _
        vbCritical, "YAELCORE-OS"
    WScript.Quit 1
End If

shell.Run """" & python & """ """ & carpeta & "\main.py""", 0, False
