$location = Get-Location
# Gets the path of the parent directory
# If the file is in the same directory as the .xlsm file, change all $parent to $location
$parent   = (get-item $location ).parent.FullName
$excel    = new-object -comobject excel.application

# Gets the files with extension .xlsm
$excelFiles = Get-ChildItem -Path $parent -Recurse -ErrorAction SilentlyContinue -Filter *.xlsm |
  Where-Object { $_.Extension -eq '.xlsm' }

if ($excelFiles.Count -gt 1) {
    $excelFiles
    "`n"
    $prompt = "Enter a file name"
    do {
        $path = (Read-Host $prompt)
        $path = "$parent\$path"
        $wrong = -NOT (Test-Path $path)
        $prompt = "This file does not exist. Try again."
    } while ($wrong)
}
else {
    # Gets the only file with the extension in the parent directory
    $path = Get-ChildItem -Path $parent -ErrorAction SilentlyContinue -Filter *.xlsm
}

$workbook = $excel.workbooks.open($path)
# Runs the macro that sorts and exports the excel file to .csv
$excel.Run("SortAndExport")
$workbook.save()
$workbook.close()

$python = Get-ChildItem -Path $parent -ErrorAction SilentlyContinue -Filter *.py
$csv = Get-ChildItem -Path $parent -ErrorAction SilentlyContinue -Filter *.csv
"`n"
# Can't figure out how to run as list, so this is easiest way
Foreach($file in $csv) {
    python $parent\$python $parent\$file
}

$excel.quit