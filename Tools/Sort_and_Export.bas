Sub SortAndExport()
    Dim MyPath As String
    Dim CSVFileName As String
    Dim WB1 As Workbook, WB2 As Workbook
    Dim Sheet1 As Worksheet
    
    Set WB1 = ActiveWorkbook
    Set Sheet1 = ActiveWorkbook.Worksheets(1)
    
    '
    ' SortDates Macro
    '
    Cells.Select
    WB1.Worksheets("Sheet1").Sort.SortFields.Clear
    WB1.Worksheets("Sheet1").Sort.SortFields.Add Key:=Range("B2:B164") _
        , SortOn:=xlSortOnValues, Order:=xlAscending, DataOption:= _
        xlSortTextAsNumbers
    With WB1.Worksheets("Sheet1").Sort
        .SetRange Range("A1:L164")
        .Header = xlYes
        .MatchCase = False
        .Orientation = xlTopToBottom
        .SortMethod = xlPinYin
        .Apply
    End With
    
    ' Autofits the rows so all content can be seen
    Cells.Select
    Cells.EntireRow.AutoFit
   
    '
    ' Export as .csv macro
    '
    ' Copys the current sheet. Must be before other stuff
    WB1.ActiveSheet.UsedRange.Copy

    ' Get name of csv file
    CSVFileName = Application.InputBox("Enter the name of the .csv file", "Enter title")
    ' Continue if not invalid (prevents type mismatch)
    If CSVFileName <> "" Then GoTo Continue
    If CSVFileName = "" Then
        MsgBox ("Invalid Name")
        Exit Sub
    Else: If CSVFileName = False Then Exit Sub
    End If
    
Continue:
    ' Adds .csv to filename if not already on it
    If Not Right(CSVFileName, 4) = ".csv" Then CSVFileName = CSVFileName & ".csv"
    FullPath = WB1.Path & "\" & CSVFileName
    
    ' Disables default alerts
    Application.DisplayAlerts = False
    ' Checks if file exists and will be overwritten
    If Dir(FullPath) <> "" Then
        If MsgBox(CSVFileName & " already exists. Do you wish to overwrite it?", vbQuestion + vbYesNo) = vbNo Then
            Exit Sub
        End If
    End If
    
    Set WB2 = Application.Workbooks.Add(1)
    ' Pastes the values from sheet 1 into a new sheet
    WB2.Sheets(1).Range("A1").PasteSpecial xlPasteValues
    
    With WB2
        .SaveAs FileName:=FullPath, FileFormat:=xlCSV, CreateBackup:=False
        .Close True
    End With
    ' Re-enables default alerts
    Application.DisplayAlerts = True
End Sub