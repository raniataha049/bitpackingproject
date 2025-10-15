param(
  [int]$Repeats = 5
)

# --- helpers ---
function Mean([double[]]$xs){ if($xs.Count -eq 0){0}else{$xs | Measure-Object -Average | % Average} }
function Std ([double[]]$xs){
  if($xs.Count -lt 2){ return 0 }
  $m = Mean $xs
  $var = ($xs | % { [math]::Pow($_ - $m, 2) } | Measure-Object -Sum | % Sum) / $xs.Count
  [math]::Sqrt($var)
}
function Ms($ts){ [math]::Round($ts.TotalMilliseconds, 3) }

# --- jeux de données ---
'0 ' * 512 | Set-Content -Encoding UTF8 zeros.txt
1..500 | % { Get-Random -Min 0 -Max 32 }   | % { $_ } | Set-Content -Encoding UTF8 k5.txt
1..500 | % { Get-Random -Min 0 -Max 4096 } | % { $_ } | Set-Content -Encoding UTF8 k12.txt
# mix: beaucoup de petits + quelques très gros
$small = 1..1000 | % { Get-Random -Min 0 -Max 64 }
$big   = 1..20   | % { Get-Random -Min 100000 -Max 1000000 }
($small + $big) -join ' ' | Set-Content -Encoding UTF8 mix.txt

$datasets = @("zeros.txt","k5.txt","k12.txt","mix.txt")
$modes = @(
  @{ name="crossing";      cmdC={ param($in,$out) "python -m cli.bitpacking_cli compress --input $in --output $out --mode crossing" }
                           cmdD={ param($in,$out) "python -m cli.bitpacking_cli decompress --input $in --output $out" } },
  @{ name="non_crossing";  cmdC={ param($in,$out) "python -m cli.bitpacking_cli compress --input $in --output $out --mode non_crossing" }
                           cmdD={ param($in,$out) "python -m cli.bitpacking_cli decompress --input $in --output $out" } },
  @{ name="overflow";      cmdC={ param($in,$out) "python -m cli.overflow_cli    compress --input $in --output $out" }
                           cmdD={ param($in,$out) "python -m cli.overflow_cli    decompress --input $in --output $out" } }
)

$rows = @()

foreach($ds in $datasets){
  foreach($m in $modes){
    Write-Host "== $($m.name) on $ds ==" -ForegroundColor Cyan
    $tC = @(); $tD = @()
    $bin = [IO.Path]::ChangeExtension($ds, ".$($m.name).bin")
    $txt = [IO.Path]::ChangeExtension($ds, ".$($m.name).restored.txt")

    # compress repeats
    1..$Repeats | % {
      $cmd = & $m.cmdC $ds $bin
      $elapsed = (Measure-Command { Invoke-Expression $cmd | Out-Null }).TotalMilliseconds
      $tC += $elapsed
    }

    # decompress repeats
    1..$Repeats | % {
      $cmd = & $m.cmdD $bin $txt
      $elapsed = (Measure-Command { Invoke-Expression $cmd | Out-Null }).TotalMilliseconds
      $tD += $elapsed
    }

    $sizeIn  = (Get-Item $ds).Length
    $sizeBin = (Get-Item $bin).Length
    $cr = if ($sizeIn -gt 0) { [math]::Round($sizeBin / $sizeIn, 3) } else { 0 }

    $row = [pscustomobject]@{
      dataset   = $ds
      mode      = $m.name
      n_runs    = $Repeats
      comp_ms_mean = [math]::Round((Mean $tC),3)
      comp_ms_std  = [math]::Round((Std  $tC),3)
      decomp_ms_mean = [math]::Round((Mean $tD),3)
      decomp_ms_std  = [math]::Round((Std  $tD),3)
      input_bytes = $sizeIn
      bin_bytes   = $sizeBin
      ratio_bin_over_input = $cr
    }
    $rows += $row
  }
}

$csv = Join-Path (Get-Location) "bench\results.csv"
$rows | Export-Csv -NoTypeInformation -Path $csv -Encoding UTF8
Write-Host "`n📊 Résumé :" -ForegroundColor Yellow
$rows | Format-Table -AutoSize
Write-Host "`nCSV écrit : $csv" -ForegroundColor Green
