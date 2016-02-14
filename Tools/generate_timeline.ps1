$location = Get-Location
# Gets the path of the parent directory
$parent   = (get-item $location ).parent.FullName
$file     = "$parent\ExcelDino.xlsm"
$excel    = new-object -comobject excel.application

$workbook = $excel.workbooks.open($file)
$worksheet = $workbook.worksheets.item(1)
# Runs the macro that sorts and exports the excel file to .csv
$excel.Run("DinoSortExport")
$workbook.save()
$workbook.close()

python "../tiki-toki.py"

$excel.quit
pause