Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the directory where this VBS script is located
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Change to the script directory
objShell.CurrentDirectory = strScriptPath

' Full path to the Python script
strPythonScript = objFSO.BuildPath(strScriptPath, "splitter.py")

' Check if splitter.py exists
If Not objFSO.FileExists(strPythonScript) Then
    MsgBox "Error: Could not find splitter.py in " & strScriptPath, vbCritical, "Spritesheet Splitter"
    WScript.Quit
End If

' Run Python script without showing command window
objShell.Run "pythonw """ & strPythonScript & """", 0, False

Set objShell = Nothing
Set objFSO = Nothing