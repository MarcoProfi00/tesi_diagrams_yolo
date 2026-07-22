param(
    [Parameter(Mandatory = $true)]
    [string]$PresentationPath,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath
)

$ErrorActionPreference = "Stop"
$presentationPathResolved = (Resolve-Path -LiteralPath $PresentationPath).Path
$outputPathResolved = [System.IO.Path]::GetFullPath($OutputPath)
[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($outputPathResolved)) | Out-Null

$powerPoint = $null
$presentation = $null

try {
    $powerPoint = New-Object -ComObject PowerPoint.Application
    $powerPoint.Visible = -1
    $powerPoint.WindowState = 2
    $presentation = $powerPoint.Presentations.Open($presentationPathResolved, 0, 0, -1)

    $rows = @()
    foreach ($slide in $presentation.Slides) {
        foreach ($shape in $slide.Shapes) {
            $text = ""
            $fontName = ""
            $fontSize = ""
            $fontColor = ""
            $bold = ""
            if ($shape.HasTextFrame -eq -1 -and $shape.TextFrame.HasText -eq -1) {
                $text = $shape.TextFrame.TextRange.Text.Replace("`r", " ").Replace("`n", " ").Trim()
                try { $fontName = $shape.TextFrame.TextRange.Font.Name } catch {}
                try { $fontSize = $shape.TextFrame.TextRange.Font.Size } catch {}
                try { $fontColor = $shape.TextFrame.TextRange.Font.Color.RGB } catch {}
                try { $bold = $shape.TextFrame.TextRange.Font.Bold } catch {}
            }

            $rows += [PSCustomObject]@{
                slide = $slide.SlideIndex
                zorder = $shape.ZOrderPosition
                id = $shape.Id
                name = $shape.Name
                type = $shape.Type
                left = [Math]::Round($shape.Left, 2)
                top = [Math]::Round($shape.Top, 2)
                width = [Math]::Round($shape.Width, 2)
                height = [Math]::Round($shape.Height, 2)
                text = $text
                font_name = $fontName
                font_size = $fontSize
                font_color = $fontColor
                bold = $bold
            }
        }
    }

    $rows | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $outputPathResolved -Encoding UTF8
    Write-Output "ShapeDump=$outputPathResolved"
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
