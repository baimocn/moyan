# 墨衍 · Windows OCR 批处理脚本（本地免费，不烧 token）
# 输入：一个目录里的 PNG 页图；输出：行级 JSON 数组 [{page, text, y0, height, rel_y}]
#
# 用法：
#   pwsh -File tools/winocr.ps1 -PngDir <目录> -OutJson <输出.json> [-MaxPages N]
# 兼容 PowerShell 5.1（Windows 自带，无额外依赖）。
param(
    [Parameter(Mandatory = $true)][string]$PngDir,
    [Parameter(Mandatory = $true)][string]$OutJson,
    # 0 = 全部
    [int]$MaxPages = 0
)

$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Foundation, ContentType = WindowsRuntime]
$null = [Windows.Storage.Streams.InMemoryRandomAccessStream, Windows.Storage.Streams, ContentType = WindowsRuntime]
$null = [Windows.Globalization.Language, Windows.Globalization, ContentType = WindowsRuntime]

# WinRT IAsyncOperation -> .NET Task -> 同步等待
$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() |
    Where-Object {
        $_.Name -eq 'AsTask' -and
        $_.GetParameters().Count -eq 1 -and
        $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
    })[0]

function Await([object]$WinRtTask, [Type]$ResultType) {
    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
    $netTask = $asTask.Invoke($null, @($WinRtTask))
    $netTask.Wait() | Out-Null
    return $netTask.Result
}

$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage([Windows.Globalization.Language]::new('zh-Hans-CN'))
if ($null -eq $engine) { throw '无法创建中文 OCR 引擎（缺 zh-Hans-CN 语言包）' }

function Ocr-Png([string]$Path) {
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    $ras = [Windows.Storage.Streams.InMemoryRandomAccessStream]::new()
    $out = [System.IO.WindowsRuntimeStreamExtensions]::AsStreamForWrite($ras)
    $out.Write($bytes, 0, $bytes.Length) | Out-Null
    $out.Flush() | Out-Null
    $ras.Seek(0) | Out-Null

    $decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($ras)) ([Windows.Graphics.Imaging.BitmapDecoder])
    $bitmap = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
    $height = $decoder.PixelHeight

    $res = Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])

    $lines = @()
    foreach ($ln in $res.Lines) {
        # 行文本：词拼接（中文分词可能插入空格，剔除行内空格）
        $text = (($ln.Words | ForEach-Object { $_.Text }) -join '')
        if ([string]::IsNullOrWhiteSpace($text)) { continue }
        # 行框：所有词框的并集
        $minX = [double]::MaxValue; $minY = [double]::MaxValue
        $maxX = [double]::MinValue; $maxY = [double]::MinValue
        foreach ($w in $ln.Words) {
            $r = $w.BoundingRect
            if ($r.X -lt $minX) { $minX = $r.X }
            if ($r.Y -lt $minY) { $minY = $r.Y }
            if (($r.X + $r.Width) -gt $maxX) { $maxX = $r.X + $r.Width }
            if (($r.Y + $r.Height) -gt $maxY) { $maxY = $r.Y + $r.Height }
        }
        $lines += [PSCustomObject]@{
            page   = 0            # 调用方填
            text   = $text
            y0     = [math]::Round($minY, 1)
            height = [math]::Round($maxY - $minY, 1)
            rel_y  = [math]::Round($minY / $height, 4)
            width  = [math]::Round($maxX - $minX, 1)
        }
    }
    return @{ lines = $lines; pageHeight = $height }
}

# ---- 主流程 ----
$pngs = Get-ChildItem -Path $PngDir -Filter '*.png' | Sort-Object { [int]($_.BaseName -replace '\D', '') }
if ($MaxPages -gt 0) { $pngs = $pngs | Select-Object -First $MaxPages }

$all = @()
$sw = [System.Diagnostics.Stopwatch]::StartNew()
$idx = 0
foreach ($png in $pngs) {
    $idx++
    $r = Ocr-Png $png.FullName
    foreach ($ln in $r.lines) {
        $ln.page = $png.BaseName -replace '\D', ''
        $all += $ln
    }
    $el = [math]::Round($sw.Elapsed.TotalSeconds, 1)
    $rate = [math]::Round($idx / $sw.Elapsed.TotalSeconds, 2)
    Write-Host ("[{0}/{1}] {2}: {3}行  用时{4}s  ({5}/s)" -f $idx, $pngs.Count, $png.Name, $r.lines.Count, $el, $rate)
}

$json = ConvertTo-Json -InputObject $all -Depth 4 -Compress
# 无 BOM UTF-8（PS5.1 的 Out-File -Encoding utf8 会写 BOM，Python 读会带 \ufeff）
[System.IO.File]::WriteAllText($OutJson, $json, (New-Object System.Text.UTF8Encoding($false)))
Write-Host ("完成：{0} 页 -> {1} 行，总耗时 {2}s，输出 {3}" -f $pngs.Count, $all.Count, [math]::Round($sw.Elapsed.TotalSeconds, 1), $OutJson)