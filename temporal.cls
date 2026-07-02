Option Explicit

Sub EjecutarScriptPython()
    Dim rutaPython As String
    Dim rutaScript As String
    Dim rutaOut As String
    Dim comando As String
    Dim wsh As Object
    Dim usuario As String
    Dim ruta As String
    Dim filePython As String
    Dim fileOut As String
    
    ' 1. Busca python.exe en PATH y en ubicaciones comunes
    usuario = UsuarioWindows()
    rutaPython = BuscarPython()
    If rutaPython = "" Then
        rutaPython = InputBox("No se encontró python.exe automáticamente. Ingresa la ruta completa a python.exe:", "Ruta Python")
        If rutaPython = "" Then
            MsgBox "No se proporcionó una ruta de Python."
            Exit Sub
        End If
        If ArchivoExiste(rutaPython) = False Then
            MsgBox "La ruta ingresada no existe: " & rutaPython
            Exit Sub
        End If
    End If
    ' MsgBox "Ruta Python: " & rutaPython
        
    ' 2. Define la ruta de tu archivo de script de Python
    ruta = ObtenerRuta()
    filePython = "prueba.py"
    Dim fileData As String
    fileData = ThisWorkbook.Name
    rutaScript = ruta & "\" & filePython
    ' rutaScript = "./prueba.ipynb"
    If ArchivoExiste(rutaScript) = False Then
        MsgBox "No existe archivo: " & rutaScript
        Exit Sub
    End If
    
    ' 3. Asegura la carpeta del script y construye el comando (citar rutas y parámetros)
    Dim scriptFolder As String
    scriptFolder = Left(rutaScript, InStrRev(rutaScript, "\") - 1)

    ' comando con rutas entre comillas — envolver toda la invocación entre comillas para cmd.exe
    ' produce: cmd.exe /c ""C:\path\python.exe" "D:\path\prueba.py" "D:\path" "archivo.xlsm""
    comando = "cmd.exe /c " & Chr(34) & Chr(34) & rutaPython & Chr(34) & " " & Chr(34) & rutaScript & Chr(34) & " " & Chr(34) & ruta & Chr(34) & " " & Chr(34) & fileData & Chr(34) & Chr(34)

    ' Mensajes de depuración: mostrar exactamente lo que se va a ejecutar

    ' Mensajes de depuración: mostrar exactamente lo que se va a ejecutar
    ' MsgBox "Depuración - comando:" & vbCrLf & comando, vbInformation, "Depuración"
    'MsgBox "Depuración - rutaScript: " & rutaScript & vbCrLf & "scriptFolder: " & scriptFolder, vbInformation, "Depuración"

    ' Además guarda el comando de depuración en un archivo para copiar/pegar fácilmente
    'Dim fso As Object
    'Dim debugPath As String
    'Dim ts As Object
    'On Error Resume Next
    'Set fso = CreateObject("Scripting.FileSystemObject")
    'If Not fso.FolderExists(ruta & "\output") Then
    '    fso.CreateFolder (ruta & "\output")
    'End If
    'debugPath = ruta & "\output\debug_cmd.txt"
    'Set ts = fso.CreateTextFile(debugPath, True)
    'ts.WriteLine "comando: " & comando
    'ts.WriteLine "rutaScript: " & rutaScript
    'ts.WriteLine "scriptFolder: " & scriptFolder
    'ts.Close
    'Set ts = Nothing
    'Set fso = Nothing
    'MsgBox "Depuración guardada en: " & debugPath, vbInformation, "Depuración"
    
    ' 4. Ejecuta el script y captura la salida de consola
    Dim exec As Object
    Dim salida As String
    Dim errores As String

    Set wsh = CreateObject("WScript.Shell")
    ' Establece la carpeta de trabajo al directorio del script para evitar que Python intente
    ' ejecutar la carpeta del workbook en lugar del script cuando hay rutas relativas
    On Error Resume Next
    wsh.CurrentDirectory = scriptFolder
    On Error GoTo 0

    Set exec = wsh.exec(comando)

    Do While exec.Status = 0
        DoEvents
    Loop

    salida = exec.StdOut.ReadAll
    errores = exec.StdErr.ReadAll
    ' 4b. Guarda stdout/stderr en un archivo de log en la carpeta output
    Dim fso2 As Object
    Dim logPath As String
    Dim ts2 As Object
    Set fso2 = CreateObject("Scripting.FileSystemObject")
    If Not fso2.FolderExists(ruta & "\output") Then
        fso2.CreateFolder (ruta & "\output")
    End If
    logPath = ruta & "\output\python_log.txt"
    Set ts2 = fso2.CreateTextFile(logPath, True)
    ts2.WriteLine "=== Python execution log ==="
    ts2.WriteLine "Timestamp: " & Now
    ts2.WriteLine "Command: " & comando
    ts2.WriteLine ""
    ts2.WriteLine "------ STDOUT ------"
    If salida <> "" Then
        ts2.WriteLine salida
    Else
        ts2.WriteLine "(no stdout)"
    End If
    ts2.WriteLine ""
    ts2.WriteLine "------ STDERR ------"
    If errores <> "" Then
        ts2.WriteLine errores
    Else
        ts2.WriteLine "(no stderr)"
    End If
    ts2.Close
    Set ts2 = Nothing
    Set fso2 = Nothing

    MsgBox "Salida escrita en: " & logPath, vbInformation, "Salida de Python"
    
    ' 5. Verifica el archivo de salida
    fileOut = "reporte.xlsx"
    rutaOut = ObtenerRuta() & "\output\" & fileOut
    If ArchivoExiste(rutaOut) = False Then
        MsgBox "No existe archivo: " & rutaOut
        Exit Sub
    End If

    Dim rutaLog As String
    rutaLog = ObtenerRuta() & "\output\python_log.txt"
    If ArchivoExiste(rutaLog) = False Then
        MsgBox "No existe archivo de log: " & rutaLog
        Exit Sub
    End If

    ' Comparar permitiendo tolerancia de ±1 minuto (ignorar segundos)
    Dim diffMin As Long
    diffMin = Abs(DateDiff("n", FileDateTime(rutaOut), FileDateTime(rutaLog)))
    If diffMin > 1 Then
        MsgBox "La fecha/hora (hasta minutos) de salida no coincide con python_log.txt." & vbCrLf & _
               "Salida: " & Format(FileDateTime(rutaOut), "yyyy-mm-dd HH:nn") & vbCrLf & _
               "Log: " & Format(FileDateTime(rutaLog), "yyyy-mm-dd HH:nn") & vbCrLf & _
               "Diferencia en minutos: " & diffMin, vbExclamation, "Verificación de timestamps"
        Exit Sub
    End If
    
    MsgBox "¡Script de Python ejecutado con éxito!", vbInformation
End Sub

Function ObtenerRuta() As String
    ' MsgBox "La ruta de este archivo es: " & ThisWorkbook.FullName
    ObtenerRuta = ThisWorkbook.Path
End Function

Function UsuarioWindows() As String

    Dim usuario As String

    UsuarioWindows = Environ("USERNAME")

    ' MsgBox "Usuario Windows: " & UsuarioWindows

End Function

Function BuscarPython() As String
    Dim pathVar As String
    Dim partes As Variant
    Dim carpeta As String
    Dim i As Long
    
    pathVar = Environ("PATH")
    If pathVar = vbNullString Then Exit Function
    
    partes = Split(pathVar, ";")
    For i = LBound(partes) To UBound(partes)
        carpeta = Trim(partes(i))
        If carpeta <> vbNullString Then
            If Right(carpeta, 1) = "\" Then
                carpeta = Left(carpeta, Len(carpeta) - 1)
            End If
            If ArchivoExiste(carpeta & "\python.exe") Then
                BuscarPython = carpeta & "\python.exe"
                Exit Function
            End If
        End If
    Next i
    
    If ArchivoExiste("C:\Users\" & UsuarioWindows() & "\AppData\Local\Microsoft\WindowsApps\python.exe") Then
        BuscarPython = "C:\Users\" & UsuarioWindows() & "\AppData\Local\Microsoft\WindowsApps\python.exe"
        Exit Function
    End If
    
    If ArchivoExiste("C:\Users\" & UsuarioWindows() & "\AppData\Local\Programs\Python\Python311\python.exe") Then
        BuscarPython = "C:\Users\" & UsuarioWindows() & "\AppData\Local\Programs\Python\Python311\python.exe"
        Exit Function
    End If
End Function

Function ArchivoExiste(rutaArchivo As String) As Boolean
    ArchivoExiste = (Dir(rutaArchivo) <> "")
End Function
