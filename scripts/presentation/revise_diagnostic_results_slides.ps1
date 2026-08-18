param(
    [string]$SourcePresentation,

    [string]$OutputPresentation,

    [switch]$LibraryOnly
)

$ErrorActionPreference = "Stop"

function Get-Rgb([int]$red, [int]$green, [int]$blue) {
    return $red + ($green -shl 8) + ($blue -shl 16)
}

$C = @{
    Navy       = Get-Rgb 11 19 32
    Text       = Get-Rgb 31 41 55
    Slate      = Get-Rgb 51 65 85
    Muted      = Get-Rgb 100 116 139
    Border     = Get-Rgb 203 213 225
    BorderSoft = Get-Rgb 226 232 240
    Track      = Get-Rgb 226 232 240
    White      = Get-Rgb 255 255 255
    Blue       = Get-Rgb 37 99 235
    BlueSoft   = Get-Rgb 239 246 255
    Green      = Get-Rgb 16 185 129
    GreenDark  = Get-Rgb 5 150 105
    GreenSoft  = Get-Rgb 236 253 245
    GreenLine  = Get-Rgb 187 247 208
    Violet     = Get-Rgb 139 92 246
    VioletSoft = Get-Rgb 245 243 255
    Amber      = Get-Rgb 245 158 11
}

$agrave = [char]0x00E0
$egrave = [char]0x00E8
$eacute = [char]0x00E9
$ograve = [char]0x00F2
$ugrave = [char]0x00F9
$times = [char]0x00D7
$middleDot = [char]0x00B7
$rightarrow = [char]0x2192
$minus = [char]0x2212

function Set-ShapeFill($shape, [int]$color) {
    $shape.Fill.Visible = -1
    $shape.Fill.Solid()
    $shape.Fill.ForeColor.RGB = $color
}

function Set-ShapeLine($shape, [int]$color, [double]$weight = 1, [bool]$visible = $true) {
    $shape.Line.Visible = if ($visible) { -1 } else { 0 }
    if ($visible) {
        $shape.Line.ForeColor.RGB = $color
        $shape.Line.Weight = $weight
    }
}

function Add-Text(
    $slide,
    [string]$text,
    [double]$left,
    [double]$top,
    [double]$width,
    [double]$height,
    [double]$fontSize,
    [int]$fontColor,
    [bool]$bold = $false,
    [string]$fontName = "Aptos",
    [int]$align = 1,
    [int]$verticalAnchor = 1
) {
    $shape = $slide.Shapes.AddTextbox(1, $left, $top, $width, $height)
    $shape.TextFrame.AutoSize = 0
    $shape.TextFrame.WordWrap = -1
    $shape.TextFrame.MarginLeft = 0
    $shape.TextFrame.MarginRight = 0
    $shape.TextFrame.MarginTop = 0
    $shape.TextFrame.MarginBottom = 0
    $shape.TextFrame.VerticalAnchor = $verticalAnchor
    $range = $shape.TextFrame.TextRange
    $range.Text = $text
    $range.Font.Name = $fontName
    $range.Font.Size = $fontSize
    $range.Font.Color.RGB = $fontColor
    $range.Font.Bold = if ($bold) { -1 } else { 0 }
    $range.ParagraphFormat.Alignment = $align
    return $shape
}

function Add-Card(
    $slide,
    [double]$left,
    [double]$top,
    [double]$width,
    [double]$height,
    [int]$fillColor,
    [int]$lineColor,
    [int]$shapeType = 5
) {
    $shape = $slide.Shapes.AddShape($shapeType, $left, $top, $width, $height)
    Set-ShapeFill $shape $fillColor
    Set-ShapeLine $shape $lineColor 1 $true
    return $shape
}

function Add-Pill(
    $slide,
    [string]$text,
    [double]$left,
    [double]$top,
    [double]$width,
    [double]$height,
    [int]$fillColor,
    [int]$fontColor,
    [double]$fontSize = 9.5
) {
    $shape = Add-Card $slide $left $top $width $height $fillColor $fillColor
    $shape.TextFrame.MarginLeft = 4
    $shape.TextFrame.MarginRight = 4
    $shape.TextFrame.MarginTop = 1
    $shape.TextFrame.MarginBottom = 1
    $shape.TextFrame.VerticalAnchor = 3
    $shape.TextFrame.TextRange.Text = $text
    $shape.TextFrame.TextRange.Font.Name = "Aptos"
    $shape.TextFrame.TextRange.Font.Size = $fontSize
    $shape.TextFrame.TextRange.Font.Color.RGB = $fontColor
    $shape.TextFrame.TextRange.Font.Bold = -1
    $shape.TextFrame.TextRange.ParagraphFormat.Alignment = 2
    return $shape
}

function Clear-SlideBody($slide) {
    for ($index = $slide.Shapes.Count; $index -ge 1; $index--) {
        $shape = $slide.Shapes.Item($index)
        $keep = $false

        if ($shape.Left -le 1 -and $shape.Top -le 1 -and $shape.Width -ge 950 -and $shape.Height -ge 530) {
            $keep = $true
        }
        elseif ($shape.Top -ge 25 -and $shape.Top -le 58 -and $shape.Left -le 50 -and $shape.HasTextFrame -eq -1) {
            $keep = $true
        }
        elseif ($shape.Top -ge 60 -and $shape.Top -le 86 -and $shape.Left -le 55 -and $shape.HasTextFrame -eq -1) {
            $keep = $true
        }
        elseif ($shape.Top -ge 86 -and $shape.Top -le 98 -and $shape.Left -le 50 -and $shape.Width -le 60) {
            $keep = $true
        }
        elseif ($shape.Top -ge 495) {
            $keep = $true
        }

        if (-not $keep) {
            $shape.Delete()
        }
    }
}

function Set-SlideHeader($slide, [string]$title, [string]$subtitle) {
    foreach ($shape in $slide.Shapes) {
        if ($shape.HasTextFrame -ne -1) {
            continue
        }
        if ($shape.Top -ge 25 -and $shape.Top -le 58 -and $shape.Left -le 50) {
            $shape.TextFrame.TextRange.Text = $title
            $shape.TextFrame.TextRange.Font.Name = "Aptos Display"
            $shape.TextFrame.TextRange.Font.Size = 28
            $shape.TextFrame.TextRange.Font.Bold = -1
            $shape.TextFrame.TextRange.Font.Color.RGB = $C.Navy
        }
        elseif ($shape.Top -ge 60 -and $shape.Top -le 86 -and $shape.Left -le 55) {
            $shape.TextFrame.TextRange.Text = $subtitle
            $shape.TextFrame.TextRange.Font.Name = "Aptos"
            $shape.TextFrame.TextRange.Font.Size = 12.5
            $shape.TextFrame.TextRange.Font.Bold = 0
            $shape.TextFrame.TextRange.Font.Color.RGB = $C.Muted
        }
    }
}

function Add-Notes($slide, [string]$notesText) {
    try {
        $placeholders = $slide.NotesPage.Shapes.Placeholders
        for ($index = 1; $index -le $placeholders.Count; $index++) {
            $placeholder = $placeholders.Item($index)
            if ($placeholder.HasTextFrame -eq -1 -and $placeholder.PlaceholderFormat.Type -eq 2) {
                $placeholder.TextFrame.TextRange.Text = $notesText
                return
            }
        }
    }
    catch {
        Write-Warning "Speaker notes not updated on slide $($slide.SlideIndex)."
    }
}

function Add-TableCell(
    $slide,
    [string]$text,
    [double]$left,
    [double]$top,
    [double]$width,
    [double]$height,
    [int]$fillColor,
    [int]$fontColor,
    [double]$fontSize,
    [bool]$bold,
    [int]$align = 1
) {
    $cell = $slide.Shapes.AddShape(1, $left, $top, $width, $height)
    Set-ShapeFill $cell $fillColor
    Set-ShapeLine $cell $C.BorderSoft 0.8 $true
    $cell.TextFrame.MarginLeft = 6
    $cell.TextFrame.MarginRight = 6
    $cell.TextFrame.MarginTop = 1
    $cell.TextFrame.MarginBottom = 1
    $cell.TextFrame.VerticalAnchor = 3
    $cell.TextFrame.TextRange.Text = $text
    $cell.TextFrame.TextRange.Font.Name = "Aptos"
    $cell.TextFrame.TextRange.Font.Size = $fontSize
    $cell.TextFrame.TextRange.Font.Color.RGB = $fontColor
    $cell.TextFrame.TextRange.Font.Bold = if ($bold) { -1 } else { 0 }
    $cell.TextFrame.TextRange.ParagraphFormat.Alignment = $align
}

function Build-ExperimentSlide($slide) {
    Clear-SlideBody $slide
    Set-SlideHeader $slide "Benchmark diagnostico: come $egrave stato costruito" "Due batch, due modalit$agrave di input e una valutazione tecnica uniforme"

    [void](Add-Card $slide 55 111 430 297 $C.White $C.Border)
    [void](Add-Text $slide "MATRICE SPERIMENTALE" 75 128 255 17 11.5 $C.GreenDark $true)
    [void](Add-Text $slide "16 circuiti $middleDot 8 modelli $middleDot 256 run" 75 154 340 23 18 $C.Navy $true "Aptos Display")

    $x = 75
    $y = 191
    $widths = @(68, 58, 205, 64)
    $headers = @("Batch", "Circuiti", "Tipologia", "Run")
    for ($i = 0; $i -lt $headers.Count; $i++) {
        Add-TableCell $slide $headers[$i] $x $y $widths[$i] 24 $C.Navy $C.White 9.2 $true 2
        $x += $widths[$i]
    }

    $rows = @(
        @("v1", "8", "IC, audio, motori, convertitori", "128"),
        @("v2", "8", "timer, display, discreti, audio", "128"),
        @("Totale", "16", "8 modelli $times 2 input", "256")
    )
    $rowTop = 215
    for ($r = 0; $r -lt $rows.Count; $r++) {
        $x = 75
        $fill = if ($r -eq 2) { $C.GreenSoft } else { $C.White }
        for ($i = 0; $i -lt $rows[$r].Count; $i++) {
            $alignment = if ($i -eq 2) { 1 } else { 2 }
            Add-TableCell $slide $rows[$r][$i] $x $rowTop $widths[$i] 27 $fill $C.Slate 8.8 ($r -eq 2) $alignment
            $x += $widths[$i]
        }
        $rowTop += 27
    }

    [void](Add-Pill $slide "JSON + datasheet" 75 316 143 30 $C.Green $C.White 9.8)
    [void](Add-Text $slide "vs" 226 322 25 17 10 $C.Muted $true "Aptos" 2)
    [void](Add-Pill $slide "JSON + immagine + datasheet" 259 316 194 30 $C.Blue $C.White 9.2)
    [void](Add-Text $slide "Ogni modello produce una diagnosi ordinata, motivata e accompagnata da controlli pratici." 75 363 370 28 10.5 $C.Slate $false)

    [void](Add-Card $slide 515 111 390 297 $C.GreenSoft $C.GreenLine)
    [void](Add-Text $slide "GPT-5.5 JUDGE" 536 128 210 17 11.5 $C.GreenDark $true)
    [void](Add-Text $slide "7 criteri $times 0-3 = 21 punti" 536 154 315 23 18 $C.Navy $true "Aptos Display")

    $criteria = @(
        "Comprensione circuito",
        "Uso datasheet",
        "Uso JSON / immagine",
        "Accuratezza diagnostica",
        "Priorit$agrave delle cause",
        "Controlli pratici",
        "Assenza di allucinazioni"
    )
    $criterionLeft = @(536, 711, 536, 711, 536, 711, 536)
    $criterionTop = @(195, 195, 231, 231, 267, 267, 303)
    $criterionWidth = @(162, 162, 162, 162, 162, 162, 337)
    for ($i = 0; $i -lt $criteria.Count; $i++) {
        [void](Add-Card $slide $criterionLeft[$i] $criterionTop[$i] $criterionWidth[$i] 28 $C.White $C.BorderSoft)
        [void](Add-Text $slide $criteria[$i] ($criterionLeft[$i] + 9) ($criterionTop[$i] + 7) ($criterionWidth[$i] - 18) 14 8.8 $C.Slate $true)
    }

    [void](Add-Pill $slide "Top-1" 536 352 58 27 $C.Blue $C.White 9.3)
    [void](Add-Pill $slide "Top-3" 601 352 58 27 $C.Violet $C.White 9.3)
    [void](Add-Pill $slide "Errori" 666 352 58 27 $C.Amber $C.White 9.3)
    [void](Add-Pill $slide "Costo" 731 352 58 27 $C.GreenDark $C.White 9.3)
    [void](Add-Pill $slide "Latenza" 796 352 68 27 $C.Navy $C.White 9.3)

    [void](Add-Card $slide 55 425 850 56 $C.BlueSoft $C.BorderSoft)
    [void](Add-Text $slide "COME SI OTTIENE IL DATO" 74 438 178 16 10.6 $C.Blue $true)
    [void](Add-Text $slide "Il judge vede JSON, immagine, datasheet, sintomo e risposta; il nome del modello non $egrave nel prompt. Gli output strutturati vengono aggregati per modello, input e circuito." 249 434 634 32 10.4 $C.Slate $false)
    [void](Add-Text $slide "Nota: una sola run per combinazione; confronto uniforme, non validazione statistica multi-rater." 249 467 634 11 8.5 $C.Muted $false)

    Add-Notes $slide "Il benchmark diagnostico usa due batch indipendenti di otto circuiti ciascuno. Ogni circuito viene eseguito con otto modelli e due modalit$agrave di input, per un totale di 256 diagnosi. GPT-5.5 valuta ogni risposta sul contesto tecnico completo con sette criteri da zero a tre. Oltre allo score su 21 vengono salvati Top-1, Top-3, errori, allucinazioni, token, latenza e costo. Il nome del modello non $egrave inserito nel prompt del judge."
}

function Add-ScoreBars($slide, [string]$model, [double]$v1, [double]$v2, [double]$top) {
    Write-Output "SCORE_BAR label $model"
    [void](Add-Text $slide $model 76 ($top + 10) 105 18 10.5 $C.Slate $true)
    $trackLeft = 185
    $trackWidth = 280

    Write-Output "SCORE_BAR shapes $model"
    [void](Add-Card $slide $trackLeft $top $trackWidth 11 $C.Track $C.Track)
    [void](Add-Card $slide $trackLeft $top ($trackWidth * ($v1 / 21.0)) 11 $C.Blue $C.Blue)
    [void](Add-Card $slide $trackLeft ($top + 18) $trackWidth 11 $C.Track $C.Track)
    [void](Add-Card $slide $trackLeft ($top + 18) ($trackWidth * ($v2 / 21.0)) 11 $C.Violet $C.Violet)

    Write-Output "SCORE_BAR values $model"
    $v1Text = $v1.ToString("0.00", [Globalization.CultureInfo]::InvariantCulture).Replace(".", ",")
    $v2Text = $v2.ToString("0.00", [Globalization.CultureInfo]::InvariantCulture).Replace(".", ",")
    [void](Add-Text $slide $v1Text 470 ($top - 3) 49 15 9.4 $C.Blue $true "Aptos" 2)
    [void](Add-Text $slide $v2Text 470 ($top + 15) 49 15 9.4 $C.Violet $true "Aptos" 2)
    Write-Output "SCORE_BAR done $model"
}

function Build-ModelResultsSlide($slide) {
    Write-Output "MODEL_RESULTS clear"
    Clear-SlideBody $slide
    Set-SlideHeader $slide "Risultati: i tre modelli pi$ugrave convincenti" "Dati da aggregate_by_model.csv dei batch v1 e v2 $middleDot 32 run per modello"

    Write-Output "MODEL_RESULTS chart"
    [void](Add-Card $slide 55 111 500 281 $C.White $C.Border)
    [void](Add-Text $slide "SCORE MEDIO PER BATCH /21" 76 129 270 17 11.5 $C.GreenDark $true)
    [void](Add-Card $slide 356 132 10 10 $C.Blue $C.Blue)
    [void](Add-Text $slide "batch v1" 372 129 62 15 9.2 $C.Slate $false)
    [void](Add-Card $slide 435 132 10 10 $C.Violet $C.Violet)
    [void](Add-Text $slide "batch v2" 451 129 62 15 9.2 $C.Slate $false)

    Write-Output "MODEL_RESULTS bar_54"
    Add-ScoreBars $slide "GPT-5.4" 19.312 18.938 168
    Write-Output "MODEL_RESULTS bar_54mini"
    Add-ScoreBars $slide "GPT-5.4-mini" 18.812 17.375 230
    Write-Output "MODEL_RESULTS bar_5mini"
    Add-ScoreBars $slide "GPT-5-mini" 17.688 17.438 292
    Write-Output "MODEL_RESULTS chart_labels"

    [void](Add-Text $slide "0" 183 351 18 13 8.5 $C.Muted $false "Aptos" 2)
    [void](Add-Text $slide "7" 272 351 18 13 8.5 $C.Muted $false "Aptos" 2)
    [void](Add-Text $slide "14" 365 351 23 13 8.5 $C.Muted $false "Aptos" 2)
    [void](Add-Text $slide "21" 455 351 23 13 8.5 $C.Muted $false "Aptos" 2)
    [void](Add-Text $slide "GPT-5.4 resta primo; i due modelli mini sono vicini e si scambiano l'ordine nel batch v2." 76 370 445 18 9.2 $C.Muted $true)

    Write-Output "MODEL_RESULTS table"
    [void](Add-Card $slide 575 111 330 281 $C.White $C.Border)
    [void](Add-Text $slide "MEDIA COMPLESSIVA V1 + V2" 594 129 270 17 11.5 $C.GreenDark $true)

    $tableLeft = 594
    $tableTop = 158
    $columnWidths = @(91, 55, 48, 48, 69)
    $headers = @("Modello", "Score", "Top-1", "Top-3", "Costo")
    $x = $tableLeft
    for ($i = 0; $i -lt $headers.Count; $i++) {
        Add-TableCell $slide $headers[$i] $x $tableTop $columnWidths[$i] 23 $C.Navy $C.White 8.4 $true 2
        $x += $columnWidths[$i]
    }

    $modelRows = @(
        @("GPT-5.4", "19,13", "78,1%", "90,6%", "`$0,0716"),
        @("5.4-mini", "18,09", "84,4%", "90,6%", "`$0,0171"),
        @("5-mini", "17,56", "62,5%", "96,9%", "`$0,0082")
    )
    $rowColors = @($C.BlueSoft, $C.GreenSoft, $C.VioletSoft)
    $rowTop = 181
    for ($r = 0; $r -lt $modelRows.Count; $r++) {
        $x = $tableLeft
        for ($i = 0; $i -lt $modelRows[$r].Count; $i++) {
            Add-TableCell $slide $modelRows[$r][$i] $x $rowTop $columnWidths[$i] 35 $rowColors[$r] $C.Slate 8.4 $true 2
            $x += $columnWidths[$i]
        }
        $rowTop += 35
    }

    [void](Add-Card $slide 594 299 292 72 $C.GreenSoft $C.GreenLine)
    [void](Add-Text $slide "GPT-5.4-mini" 610 312 130 17 12 $C.GreenDark $true)
    [void](Add-Text $slide "$minus 1,03 punti rispetto a GPT-5.4" 610 336 250 15 9.8 $C.Slate $true)
    [void](Add-Text $slide "circa 76% di costo in meno $middleDot Top-1 pi$ugrave alta" 610 354 258 14 9.3 $C.Slate $false)

    Write-Output "MODEL_RESULTS conclusion"
    [void](Add-Card $slide 55 408 850 74 $C.GreenSoft $C.GreenLine)
    [void](Add-Text $slide "LETTURA FINALE" 75 424 130 16 10.7 $C.GreenDark $true)
    [void](Add-Text $slide "GPT-5.4 massimizza la qualit$agrave. GPT-5.4-mini $egrave il miglior equilibrio qualit$agrave/costo. GPT-5-mini costa ancora meno e raggiunge la Top-3 pi$ugrave alta, ma ordina peggio la causa principale." 200 419 680 35 11 $C.Slate $true)
    [void](Add-Text $slide "Costo medio del solo modello generativo; costo del judge escluso." 200 461 680 12 8.6 $C.Muted $false)

    Write-Output "MODEL_RESULTS notes"
    Add-Notes $slide "GPT-5.4 resta il modello con la qualit$agrave pi$ugrave alta in entrambi i batch. I due modelli mini sono molto vicini e nel batch v2 GPT-5-mini supera di poco GPT-5.4-mini. Sulla media complessiva, GPT-5.4 raggiunge 19,13 su 21; GPT-5.4-mini scende di circa un punto, ma costa circa il 76 per cento in meno e ha la Top-1 aggregata pi$ugrave alta. GPT-5-mini ottiene 17,56 su 21, ha il costo pi$ugrave basso e una Top-3 del 96,9 per cento, ma una Top-1 inferiore: tende quindi a includere la causa corretta senza sempre metterla al primo posto."
    Write-Output "MODEL_RESULTS done"
}

if ($LibraryOnly) {
    return
}

if ([string]::IsNullOrWhiteSpace($SourcePresentation) -or [string]::IsNullOrWhiteSpace($OutputPresentation)) {
    throw "SourcePresentation and OutputPresentation are required unless LibraryOnly is set."
}

$sourcePath = (Resolve-Path -LiteralPath $SourcePresentation).Path
$outputPath = [IO.Path]::GetFullPath($OutputPresentation)
[IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($outputPath)) | Out-Null

$powerPoint = $null
$presentation = $null

try {
    Write-Output "STEP open_powerpoint"
    $powerPoint = New-Object -ComObject PowerPoint.Application
    $powerPoint.Visible = -1
    $powerPoint.WindowState = 2
    $powerPoint.DisplayAlerts = 1
    Write-Output "STEP open_presentation"
    # Open as an untitled copy. This avoids inheriting a read-only lock when the
    # source deck is already present in a background PowerPoint instance.
    $presentation = $powerPoint.Presentations.Open($sourcePath, 0, -1, -1)

    Write-Output "STEP build_experiment"
    Build-ExperimentSlide $presentation.Slides.Item(5)
    Write-Output "STEP build_results"
    Build-ModelResultsSlide $presentation.Slides.Item(6)

    Write-Output "STEP save"
    try {
        $presentation.SaveAs($outputPath, 24)
    }
    catch {
        if (-not (Test-Path -LiteralPath $outputPath)) {
            throw
        }
        Write-Warning "PowerPoint returned an error after creating the output; the file will be validated separately."
    }

    Write-Output "Saved=$outputPath"
    Write-Output "Slides=$($presentation.Slides.Count)"
}
finally {
    if ($presentation) {
        $presentation.Close()
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($presentation)
    }
    if ($powerPoint) {
        $powerPoint.Quit()
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($powerPoint)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
