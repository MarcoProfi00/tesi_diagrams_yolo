param(
    [Parameter(Mandatory = $true)]
    [string]$PresentationPath,

    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory
)

$ErrorActionPreference = "Stop"

$resolvedPresentation = (Resolve-Path -LiteralPath $PresentationPath).Path
$resolvedOutput = [System.IO.Path]::GetFullPath($OutputDirectory)
[System.IO.Directory]::CreateDirectory($resolvedOutput) | Out-Null

$powerPoint = $null
$presentation = $null

try {
    $powerPoint = New-Object -ComObject PowerPoint.Application
    $powerPoint.Visible = -1
    $powerPoint.WindowState = 2
    $presentation = $powerPoint.Presentations.Open($resolvedPresentation, 0, 0, -1)

    $slideSummaries = @()
    foreach ($slide in $presentation.Slides) {
        $texts = @()
        foreach ($shape in $slide.Shapes) {
            if ($shape.HasTextFrame -eq -1 -and $shape.TextFrame.HasText -eq -1) {
                $value = $shape.TextFrame.TextRange.Text.Trim()
                if ($value) {
                    $texts += $value
                }
            }
        }

        $slideSummaries += [PSCustomObject]@{
            slide = $slide.SlideIndex
            layout = $slide.CustomLayout.Name
            background_rgb = if ($slide.FollowMasterBackground -eq 0) { $slide.Background.Fill.ForeColor.RGB } else { "master" }
            text = ($texts -join " | ")
        }
    }

    $summaryPath = Join-Path $resolvedOutput "slides_summary.json"
    $slideSummaries | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $summaryPath -Encoding UTF8

    $presentation.Export($resolvedOutput, "PNG", 1600, 900)
    Write-Output "Slides=$($presentation.Slides.Count)"
    Write-Output "Summary=$summaryPath"
    Write-Output "RenderDirectory=$resolvedOutput"
}
finally {
    if ($presentation) {
        $presentation.Close()
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($presentation)
    }
    if ($powerPoint) {
        $powerPoint.Quit()
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($powerPoint)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
