param(
    [Parameter(Mandatory = $true)]
    [string]$SourcePresentation,

    [Parameter(Mandatory = $true)]
    [string]$OutputPresentation
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
    Red        = Get-Rgb 239 68 68
    Gray       = Get-Rgb 148 163 184
}

$agrave = [char]0x00E0
$egrave = [char]0x00E8
$eacute = [char]0x00E9
$igrave = [char]0x00EC
$ograve = [char]0x00F2
$ugrave = [char]0x00F9
$times = [char]0x00D7
$plusminus = [char]0x00B1
$leftright = [char]0x2194
$rightarrow = [char]0x2192
$middleDot = [char]0x00B7
$minus = [char]0x2212

function Set-ShapeFill($shape, [int]$color, [double]$transparency = 0) {
    $shape.Fill.Visible = -1
    $shape.Fill.Solid()
    $shape.Fill.ForeColor.RGB = $color
    $shape.Fill.Transparency = $transparency
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
    [double]$fontSize = 12,
    [int]$fontColor = 0,
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

function Add-RoundedCard(
    $slide,
    [double]$left,
    [double]$top,
    [double]$width,
    [double]$height,
    [int]$fillColor,
    [int]$lineColor,
    [double]$radiusType = 5
) {
    $shape = $slide.Shapes.AddShape($radiusType, $left, $top, $width, $height)
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
    [double]$fontSize = 10,
    [bool]$bold = $true
) {
    $shape = Add-RoundedCard $slide $left $top $width $height $fillColor $fillColor
    $shape.TextFrame.MarginLeft = 4
    $shape.TextFrame.MarginRight = 4
    $shape.TextFrame.MarginTop = 1
    $shape.TextFrame.MarginBottom = 1
    $shape.TextFrame.VerticalAnchor = 3
    $shape.TextFrame.TextRange.Text = $text
    $shape.TextFrame.TextRange.Font.Name = "Aptos"
    $shape.TextFrame.TextRange.Font.Size = $fontSize
    $shape.TextFrame.TextRange.Font.Color.RGB = $fontColor
    $shape.TextFrame.TextRange.Font.Bold = if ($bold) { -1 } else { 0 }
    $shape.TextFrame.TextRange.ParagraphFormat.Alignment = 2
    return $shape
}

function Add-Bullet(
    $slide,
    [string]$text,
    [double]$left,
    [double]$top,
    [double]$width,
    [double]$height,
    [int]$bulletColor,
    [double]$fontSize = 11.5,
    [int]$fontColor = 0
) {
    $dot = $slide.Shapes.AddShape(9, $left, $top + 5, 5.5, 5.5)
    Set-ShapeFill $dot $bulletColor
    Set-ShapeLine $dot $bulletColor 0 $false
    [void](Add-Text $slide $text ($left + 13) $top ($width - 13) $height $fontSize $fontColor $false "Aptos" 1 1)
}

function Add-Arrow($slide, [double]$x1, [double]$y1, [double]$x2, [double]$y2, [int]$color) {
    $line = $slide.Shapes.AddLine($x1, $y1, $x2, $y2)
    $line.Line.ForeColor.RGB = $color
    $line.Line.Weight = 1.5
    $line.Line.EndArrowheadStyle = 3
    return $line
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

function Replace-SlideBackground($slide, [string]$backgroundAsset) {
    for ($index = $slide.Shapes.Count; $index -ge 1; $index--) {
        $shape = $slide.Shapes.Item($index)
        if ($shape.Left -le 1 -and $shape.Top -le 1 -and $shape.Width -ge 950 -and $shape.Height -ge 530) {
            $shape.Delete()
        }
    }

    $picture = $slide.Shapes.AddPicture($backgroundAsset, 0, -1, 0, 0, 960, 540)
    $picture.ZOrder(1)
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
        Write-Warning "Speaker notes not added to slide $($slide.SlideIndex): $($_.Exception.Message)"
    }
}

function Build-ProtocolSlide($slide) {
    Clear-SlideBody $slide
    Replace-SlideBackground $slide $script:BackgroundAsset
    Set-SlideHeader $slide "Verifica dell'output della Pipeline 1.0" "Due quality gate: fedelt$agrave topologica e utilit$agrave per il troubleshooting"

    [void](Add-RoundedCard $slide 55 108 850 38 $C.BlueSoft $C.BorderSoft)
    [void](Add-Text $slide "Prima di usare il Graph JSON nelle fasi successive, l'output viene verificato su due livelli indipendenti." 74 118 812 17 12 $C.Slate $true "Aptos" 1 1)

    [void](Add-RoundedCard $slide 55 162 400 245 $C.White $C.Border)
    [void](Add-Pill $slide "01  IMAGE $leftright GRAPH" 76 180 169 25 $C.GreenDark $C.White 10.5 $true)
    [void](Add-Text $slide "Fedelt$agrave topologica" 76 216 335 25 19 $C.Navy $true "Aptos Display" 1 1)

    [void](Add-Pill $slide "Immagine" 76 257 94 34 $C.Blue $C.White 10.5 $true)
    [void](Add-Text $slide "+" 181 262 18 20 16 $C.Muted $true "Aptos" 2 1)
    [void](Add-Pill $slide "Graph JSON" 208 257 101 34 $C.Green $C.White 10.5 $true)
    [void](Add-Arrow $slide 319 274 345 274 $C.Gray)
    [void](Add-Pill $slide "GPT-5.4`njudge" 354 252 78 44 $C.Navy $C.White 10.5 $true)

    Add-Bullet $slide "4 batch $middleDot 38 circuiti verificati" 77 314 345 20 $C.Green 11.5 $C.Slate
    Add-Bullet $slide "Controllo di terminali, pin e connessioni" 77 340 345 20 $C.Green 11.5 $C.Slate
    Add-Bullet $slide "Solo ci$ograve che $egrave visibile: nessun datasheet" 77 366 345 20 $C.Green 11.5 $C.Slate

    [void](Add-RoundedCard $slide 505 162 400 245 $C.White $C.Border)
    [void](Add-Pill $slide "02  DIAGNOSI SUI SINTOMI" 526 180 197 25 $C.Violet $C.White 10.5 $true)
    [void](Add-Text $slide "Utilit$agrave diagnostica" 526 216 335 25 19 $C.Navy $true "Aptos Display" 1 1)

    [void](Add-Pill $slide "JSON +`ndatasheet" 526 251 92 47 $C.Green $C.White 9.8 $true)
    [void](Add-Pill $slide "JSON + immagine`n+ datasheet" 626 251 105 47 $C.Blue $C.White 9.4 $true)
    [void](Add-Arrow $slide 741 274 765 274 $C.Gray)
    [void](Add-Pill $slide "8 GPT $rightarrow`nGPT-5.5 judge" 774 251 108 47 $C.Navy $C.White 9.7 $true)

    Add-Bullet $slide "2 batch $middleDot 16 circuiti $middleDot 256 diagnosi" 527 314 345 20 $C.Violet 11.5 $C.Slate
    Add-Bullet $slide "Stesso sintomo e doppia modalit$agrave di input" 527 340 345 20 $C.Violet 11.5 $C.Slate
    Add-Bullet $slide "Risposta, token, latenza e costo salvati" 527 366 345 20 $C.Violet 11.5 $C.Slate

    [void](Add-RoundedCard $slide 55 424 850 58 $C.GreenSoft $C.GreenLine)
    [void](Add-Text $slide "Perch$eacute due test?" 75 438 135 17 11.5 $C.GreenDark $true "Aptos" 1 1)
    [void](Add-Text $slide "Un grafo pu$ograve essere fedele all'immagine ma non ancora simulabile. Il primo gate misura la topologia; il secondo misura quanto quella struttura supporta una diagnosi tecnica." 205 435 674 32 11.2 $C.Slate $false "Aptos" 1 1)

    Add-Notes $slide "Questa slide distingue due verifiche. La prima confronta direttamente immagine e Graph JSON su 38 circuiti: non giudica se il circuito funziona, ma solo se il grafo descrive i fili e i terminali visibili. La seconda misura l'utilit$agrave diagnostica su 16 circuiti: otto modelli ricevono il JSON con o senza immagine e le risposte vengono poi valutate da un judge separato. In totale sono state analizzate 256 diagnosi."
}

function Build-JudgeSlide($slide) {
    Clear-SlideBody $slide
    Replace-SlideBackground $slide $script:BackgroundAsset
    Set-SlideHeader $slide "GPT judge: prompt, regole e valutazione" "Output JSON vincolato per rendere il confronto uniforme e ripetibile"

    [void](Add-RoundedCard $slide 55 111 365 315 $C.Navy $C.Navy)
    [void](Add-Text $slide "PROMPT IMAGE $leftright GRAPH" 77 130 300 18 11.5 $C.Green $true "Aptos" 1 1)
    [void](Add-Text $slide "Input al judge multimodale" 77 157 300 24 18 $C.White $true "Aptos Display" 1 1)

    [void](Add-Pill $slide "Immagine originale" 77 198 138 29 $C.Blue $C.White 10 $true)
    [void](Add-Pill $slide "Graph JSON" 226 198 105 29 $C.Green $C.White 10 $true)
    [void](Add-Pill $slide "YAML terminali" 77 237 138 29 $C.Violet $C.White 10 $true)
    [void](Add-Pill $slide "Regole rigorose" 226 237 126 29 $C.Slate $C.White 10 $true)

    [void](Add-Arrow $slide 215 286 215 308 $C.Gray)
    [void](Add-Text $slide "I collegamenti terminale-terminale`ndichiarati nel JSON coincidono con l'immagine?" 77 315 298 42 12.5 $C.White $true "Aptos" 2 1)
    [void](Add-Text $slide "Niente datasheet, valori o giudizio sul funzionamento.`nLe ambiguit$agrave finiscono in uncertain_points." 77 374 298 34 9.7 $C.Border $false "Aptos" 1 1)

    [void](Add-Text $slide "SCORING TOPOLOGICO /100" 456 112 260 18 11.5 $C.GreenDark $true "Aptos" 1 1)
    $scoreRows = @(
        @{ Label = "Componenti endpoint"; Value = "10"; Color = $C.Blue },
        @{ Label = "Terminali e pin"; Value = "25"; Color = $C.Violet },
        @{ Label = "Connessioni del graph"; Value = "55"; Color = $C.Green },
        @{ Label = "Semantica visibile"; Value = "10"; Color = $C.Gray }
    )
    $rowTop = 143
    foreach ($row in $scoreRows) {
        [void](Add-RoundedCard $slide 456 $rowTop 330 35 $C.White $C.BorderSoft)
        [void](Add-RoundedCard $slide 456 $rowTop 6 35 $row.Color $row.Color 1)
        [void](Add-Text $slide $row.Label 476 ($rowTop + 9) 223 16 10.8 $C.Slate $true "Aptos" 1 1)
        [void](Add-Pill $slide $row.Value 728 ($rowTop + 6) 42 23 $row.Color $C.White 10.5 $true)
        $rowTop += 42
    }

    [void](Add-Text $slide "DECISIONE" 806 112 90 18 11.5 $C.GreenDark $true "Aptos" 1 1)
    [void](Add-Pill $slide "VERY HIGH`n90-100" 806 143 90 38 $C.GreenDark $C.White 9.3 $true)
    [void](Add-Pill $slide "HIGH`n75-89" 806 187 90 38 $C.Green $C.White 9.3 $true)
    [void](Add-Pill $slide "MEDIUM`n55-74" 806 231 90 38 $C.Amber $C.White 9.3 $true)
    [void](Add-Pill $slide "LOW`n0-54" 806 275 90 38 $C.Red $C.White 9.3 $true)

    [void](Add-RoundedCard $slide 456 330 440 96 $C.GreenSoft $C.GreenLine)
    $diagnosticHeading = "SECONDO JUDGE: QUALIT{0} DIAGNOSTICA /21" -f ([string]$agrave).ToUpper()
    [void](Add-Text $slide $diagnosticHeading 474 344 390 17 10.7 $C.GreenDark $true "Aptos" 1 1)
    [void](Add-Text $slide "7 criteri $times 0-3: comprensione $middleDot datasheet $middleDot uso input $middleDot accuratezza`npriorit$agrave $middleDot controlli pratici $middleDot assenza di allucinazioni" 474 369 403 31 10.1 $C.Slate $false "Aptos" 1 1)
    [void](Add-Text $slide "Output: score, verdetto, Top-1/Top-3, errori gravi e allucinazioni." 474 406 403 14 9.4 $C.Slate $true "Aptos" 1 1)

    [void](Add-RoundedCard $slide 55 442 841 39 $C.White $C.BorderSoft)
    [void](Add-Pill $slide "JSON judge" 73 450 91 23 $C.Navy $C.White 9.5 $true)
    [void](Add-Arrow $slide 174 462 207 462 $C.Gray)
    [void](Add-Pill $slide "CSV + report" 216 450 99 23 $C.Blue $C.White 9.5 $true)
    [void](Add-Arrow $slide 325 462 358 462 $C.Gray)
    [void](Add-Pill $slide "Aggregazioni" 367 450 104 23 $C.Violet $C.White 9.5 $true)
    [void](Add-Arrow $slide 481 462 514 462 $C.Gray)
    [void](Add-Pill $slide "Grafici" 523 450 79 23 $C.Green $C.White 9.5 $true)
    [void](Add-Text $slide "Critici / maggiori / minori $middleDot usable_as_graph_base" 630 454 248 17 9.5 $C.Muted $true "Aptos" 1 1)

    Add-Notes $slide "Il prompt del primo judge limita esplicitamente il compito alla fedelt$agrave topologica. L'immagine $egrave la fonte visiva principale, il JSON $egrave l'ipotesi da verificare e il file YAML serve solo come vocabolario dei terminali. Il punteggio assegna 55 punti su 100 alle connessioni del grafo, quindi gli errori topologici pesano pi$ugrave degli errori semantici. Il secondo judge, GPT-5.5, valuta invece le diagnosi su sette criteri da zero a tre; nel prompt non viene inserito il nome del modello valutato. I risultati strutturati vengono convertiti in CSV, report e grafici."
}

function Add-FidelityBar($slide, [string]$label, [double]$value, [double]$top) {
    [void](Add-Text $slide $label 78 ($top - 1) 35 16 10.5 $C.Slate $true "Aptos" 1 1)
    [void](Add-RoundedCard $slide 117 $top 235 17 $C.Track $C.Track)
    $barWidth = 235 * ($value / 100.0)
    [void](Add-RoundedCard $slide 117 $top $barWidth 17 $C.Green $C.Green)
    [void](Add-Text $slide ($value.ToString("0.0", [System.Globalization.CultureInfo]::InvariantCulture).Replace(".", ",")) 361 ($top - 1) 48 17 10.5 $C.Navy $true "Aptos" 2 1)
}

function Add-DiagnosticBar($slide, [string]$label, [double]$jsonValue, [double]$imageValue, [double]$top) {
    [void](Add-Text $slide $label 510 ($top + 5) 64 18 10.5 $C.Slate $true "Aptos" 1 1)
    $trackWidth = 265
    [void](Add-RoundedCard $slide 579 $top $trackWidth 10 $C.Track $C.Track)
    [void](Add-RoundedCard $slide 579 $top ($trackWidth * ($jsonValue / 21.0)) 10 $C.Blue $C.Blue)
    [void](Add-RoundedCard $slide 579 ($top + 17) $trackWidth 10 $C.Track $C.Track)
    [void](Add-RoundedCard $slide 579 ($top + 17) ($trackWidth * ($imageValue / 21.0)) 10 $C.Violet $C.Violet)
    $jsonText = $jsonValue.ToString("0.00", [System.Globalization.CultureInfo]::InvariantCulture).Replace(".", ",")
    $imageText = $imageValue.ToString("0.00", [System.Globalization.CultureInfo]::InvariantCulture).Replace(".", ",")
    [void](Add-Text $slide $jsonText 849 ($top - 3) 44 15 9.3 $C.Blue $true "Aptos" 2 1)
    [void](Add-Text $slide $imageText 849 ($top + 14) 44 15 9.3 $C.Violet $true "Aptos" 2 1)
}

function Build-ResultsSlide($slide) {
    Clear-SlideBody $slide
    Replace-SlideBackground $slide $script:BackgroundAsset
    Set-SlideHeader $slide "Risultati della verifica" "Graph JSON generalmente fedele; l'immagine $egrave utile ma non sempre determinante"

    [void](Add-RoundedCard $slide 55 112 390 278 $C.White $C.Border)
    $fidelityHeading = "FEDELT{0} IMMAGINE {1} GRAPH" -f ([string]$agrave).ToUpper(), $leftright
    [void](Add-Text $slide $fidelityHeading 76 130 315 18 11.5 $C.GreenDark $true "Aptos" 1 1)
    [void](Add-Text $slide "Score medio per batch /100" 76 158 260 19 15.5 $C.Navy $true "Aptos Display" 1 1)
    Add-FidelityBar $slide "A" 93.0 196
    Add-FidelityBar $slide "B" 89.5 226
    Add-FidelityBar $slide "C1" 93.6 256
    Add-FidelityBar $slide "C2" 93.62 286
    [void](Add-Pill $slide "92,4/100 media" 76 329 128 25 $C.GreenDark $C.White 10 $true)
    [void](Add-Pill $slide "38/38 usabili" 214 329 112 25 $C.Blue $C.White 10 $true)
    [void](Add-Text $slide "32 VERY HIGH $middleDot 4 HIGH $middleDot 2 MEDIUM $middleDot 0 LOW" 76 367 325 14 9.5 $C.Muted $true "Aptos" 1 1)

    [void](Add-RoundedCard $slide 475 112 430 278 $C.White $C.Border)
    [void](Add-Text $slide "DIAGNOSI: QUANTO AGGIUNGE L'IMMAGINE?" 498 130 342 18 11.5 $C.GreenDark $true "Aptos" 1 1)
    [void](Add-Text $slide "Score medio /21" 498 158 180 19 15.5 $C.Navy $true "Aptos Display" 1 1)
    [void](Add-Pill $slide "256 run" 817 151 64 24 $C.Navy $C.White 9.6 $true)

    [void](Add-RoundedCard $slide 498 188 10 10 $C.Blue $C.Blue)
    [void](Add-Text $slide "JSON + datasheet" 514 185 112 15 9.3 $C.Slate $false "Aptos" 1 1)
    [void](Add-RoundedCard $slide 641 188 10 10 $C.Violet $C.Violet)
    [void](Add-Text $slide "JSON + immagine" 657 185 116 15 9.3 $C.Slate $false "Aptos" 1 1)

    Add-DiagnosticBar $slide "Batch v1" 15.672 15.938 218
    Add-DiagnosticBar $slide "Batch v2" 14.938 15.312 272

    [void](Add-Pill $slide "Delta score +0,32" 500 328 122 25 $C.Green $C.White 9.7 $true)
    [void](Add-Pill $slide "Top-1 +3,9 pp" 632 328 111 25 $C.Blue $C.White 9.7 $true)
    [void](Add-Pill $slide "Top-3 85,2%" 753 328 112 25 $C.Violet $C.White 9.7 $true)
    [void](Add-Text $slide "Migliore qualit${agrave}: GPT-5.4 = 19,13/21; i modelli mini riducono il costo." 500 367 365 14 9.5 $C.Muted $true "Aptos" 1 1)

    [void](Add-RoundedCard $slide 55 408 850 72 $C.GreenSoft $C.GreenLine)
    [void](Add-Text $slide "MESSAGGIO CHIAVE" 75 423 143 16 10.8 $C.GreenDark $true "Aptos" 1 1)
    [void](Add-Text $slide "Il Graph JSON conserva gi$agrave gran parte dell'informazione necessaria al troubleshooting. L'immagine $egrave complementare: pu$ograve aiutare, essere neutra o introdurre rumore a seconda del circuito e del modello." 213 419 666 34 11.2 $C.Slate $true "Aptos" 1 1)
    [void](Add-Text $slide "Limite: un solo judge e una sola run per combinazione; benchmark uniforme, non validazione statistica multi-rater." 213 458 666 13 8.8 $C.Muted $false "Aptos" 1 1)

    Add-Notes $slide "La verifica image-graph produce una media complessiva di circa 92,4 su 100. Tutti i 38 grafi sono giudicati utilizzabili come base: 32 VERY HIGH, quattro HIGH e due MEDIUM, senza casi LOW. Nel benchmark diagnostico, aggregando i due batch, aggiungere l'immagine porta lo score medio da 15,30 a 15,63 su 21. Il miglioramento medio $egrave piccolo e non sistematico: nel batch v1 la Top-1 peggiora, mentre nel batch v2 migliora. Il risultato sostiene quindi che il JSON sia gi$agrave informativo e che l'immagine vada considerata come supporto complementare."
}

function Update-SlideNumbers($presentation) {
    foreach ($slide in $presentation.Slides) {
        $pageNumber = "{0:D2}" -f $slide.SlideIndex
        foreach ($shape in $slide.Shapes) {
            if ($shape.HasTextFrame -eq -1 -and $shape.Top -ge 485 -and $shape.Left -ge 850) {
                $shape.TextFrame.TextRange.Text = $pageNumber
                $shape.TextFrame.TextRange.Font.Name = "Aptos"
                $shape.TextFrame.TextRange.Font.Size = 8.5
                $shape.TextFrame.TextRange.Font.Bold = -1
            }
        }
    }
}

$sourcePath = (Resolve-Path -LiteralPath $SourcePresentation).Path
$outputPath = [System.IO.Path]::GetFullPath($OutputPresentation)
[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($outputPath)) | Out-Null

$script:BackgroundAsset = Join-Path ([System.IO.Path]::GetDirectoryName($outputPath)) "_light_template_background.png"
Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [System.IO.Compression.ZipFile]::OpenRead($sourcePath)
try {
    $entry = $archive.GetEntry("ppt/media/image4.png")
    if (-not $entry) {
        throw "Light template background not found in the presentation package."
    }
    $inputStream = $entry.Open()
    try {
        $outputStream = [System.IO.File]::Create($script:BackgroundAsset)
        try {
            $inputStream.CopyTo($outputStream)
        }
        finally {
            $outputStream.Dispose()
        }
    }
    finally {
        $inputStream.Dispose()
    }
}
finally {
    $archive.Dispose()
}

$powerPoint = $null
$presentation = $null

try {
    Write-Output "STEP open_powerpoint"
    $powerPoint = New-Object -ComObject PowerPoint.Application
    $powerPoint.Visible = -1
    $powerPoint.WindowState = 2
    $powerPoint.DisplayAlerts = 1
    Write-Output "STEP open_presentation"
    $presentation = $powerPoint.Presentations.Open($sourcePath, 0, 0, -1)

    $templateSlide = $presentation.Slides.Item(5)
    Write-Output "STEP duplicate_slides"
    $newSlide1 = $templateSlide.Duplicate().Item(1)
    $newSlide1.MoveTo(5)

    $newSlide2 = $templateSlide.Duplicate().Item(1)
    $newSlide2.MoveTo(6)

    Write-Output "STEP build_protocol"
    Build-ProtocolSlide $presentation.Slides.Item(5)
    Write-Output "STEP build_judge"
    Build-JudgeSlide $presentation.Slides.Item(6)

    # Original slide 6 is now slide 8; keep the slide but replace the compact
    # validation summary with the richer result view.
    Write-Output "STEP build_results"
    Build-ResultsSlide $presentation.Slides.Item(8)

    Write-Output "STEP update_numbers"
    Update-SlideNumbers $presentation

    Write-Output "STEP save_copy"
    $presentation.SaveCopyAs($outputPath, 24, 0)
    Write-Output "STEP saved"
    Write-Output "Saved=$outputPath"
    Write-Output "Slides=$($presentation.Slides.Count)"
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
