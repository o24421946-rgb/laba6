$ErrorActionPreference = "Stop"
$workspace = "C:\Users\denis\OneDrive\Рабочий стол\Система контроля версий (laba6)"
Set-Location -LiteralPath $workspace
git fetch origin
git merge origin/feature/logic

