$excel = new-object -comobject excel.application

$workbook = $excel.workbooks.open("Dinosaur.xlsm")
$worksheet = $workbook.worksheets.item(1)
$excel.Run("SortAndExport")
$workbook.save()
$workbook.close()

python "git version.py"

$excel.quit
pause
