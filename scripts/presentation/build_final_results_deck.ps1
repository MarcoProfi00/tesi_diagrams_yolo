param(
    [Parameter(Mandatory = $true)]
    [string]$SourcePresentation,

    [Parameter(Mandatory = $true)]
    [string]$OutputPresentation
)

$ErrorActionPreference = "Stop"

$requestedSource = $SourcePresentation
$requestedOutput = $OutputPresentation
$libraryPath = Join-Path $PSScriptRoot "revise_diagnostic_results_slides.ps1"
. $libraryPath -LibraryOnly
$SourcePresentation = $requestedSource
$OutputPresentation = $requestedOutput

function Add-LightTemplateSkeleton($slide, [string]$backgroundAsset) {
    # A solid F8FAFC canvas matches the visible base of the internal template
    # and avoids introducing a linked-image relationship on newly added slides.
    $canvas = $slide.Shapes.AddShape(1, 0, 0, 960, 540)
    Set-ShapeFill $canvas (Get-Rgb 248 250 252)
    Set-ShapeLine $canvas (Get-Rgb 248 250 252) 0 $false
    $canvas.ZOrder(1)

    [void](Add-Text $slide "Titolo" 41.76 30.24 691.2 34.56 28 $C.Navy $true "Aptos Display")
    [void](Add-Text $slide "Sottotitolo" 43.2 66.96 763.2 20.16 12.5 $C.Muted $false "Aptos")

    $accent = $slide.Shapes.AddShape(1, 41.76, 90.72, 46.8, 3.96)
    Set-ShapeFill $accent $C.Green
    Set-ShapeLine $accent $C.Green 0 $false

    [void](Add-Text $slide "Panoramica percorso di tesi" 39.6 512.64 424.8 12.96 7.5 $C.Muted $false "Aptos")
    [void](Add-Text $slide "00" 891.36 505.44 30.24 15.84 8.5 $C.Muted $true "Aptos" 2)

    $footerLine = $slide.Shapes.AddLine(39.6, 499.68, 919.44, 499.68)
    $footerLine.Line.ForeColor.RGB = $C.Border
    $footerLine.Line.Weight = 0.8
}

function Add-SummaryFidelityBar($slide, [string]$label, [double]$value, [double]$top) {
    [void](Add-Text $slide $label 78 ($top - 1) 35 16 10.3 $C.Slate $true)
    [void](Add-Card $slide 117 $top 235 17 $C.Track $C.Track)
    [void](Add-Card $slide 117 $top (235 * ($value / 100.0)) 17 $C.Green $C.Green)
    $valueText = $value.ToString("0.0", [Globalization.CultureInfo]::InvariantCulture).Replace(".", ",")
    [void](Add-Text $slide $valueText 361 ($top - 1) 48 17 10.3 $C.Navy $true "Aptos" 2)
}

function Add-SummaryDiagnosticBar($slide, [string]$label, [double]$jsonValue, [double]$imageValue, [double]$top) {
    [void](Add-Text $slide $label 510 ($top + 5) 64 18 10.3 $C.Slate $true)
    $trackWidth = 265
    [void](Add-Card $slide 579 $top $trackWidth 10 $C.Track $C.Track)
    [void](Add-Card $slide 579 $top ($trackWidth * ($jsonValue / 21.0)) 10 $C.Blue $C.Blue)
    [void](Add-Card $slide 579 ($top + 17) $trackWidth 10 $C.Track $C.Track)
    [void](Add-Card $slide 579 ($top + 17) ($trackWidth * ($imageValue / 21.0)) 10 $C.Violet $C.Violet)
    $jsonText = $jsonValue.ToString("0.00", [Globalization.CultureInfo]::InvariantCulture).Replace(".", ",")
    $imageText = $imageValue.ToString("0.00", [Globalization.CultureInfo]::InvariantCulture).Replace(".", ",")
    [void](Add-Text $slide $jsonText 849 ($top - 3) 44 15 9.3 $C.Blue $true "Aptos" 2)
    [void](Add-Text $slide $imageText 849 ($top + 14) 44 15 9.3 $C.Violet $true "Aptos" 2)
}

function Build-VerificationSummarySlide($slide) {
    Clear-SlideBody $slide
    Set-SlideHeader $slide "Verifica complessiva della Pipeline 1.0" "Fedelt$agrave image $rightarrow graph e utilit$agrave diagnostica: risultati aggregati"

    [void](Add-Card $slide 55 112 390 278 $C.White $C.Border)
    [void](Add-Text $slide "FEDELT$($agrave.ToString().ToUpper()) IMAGE $rightarrow GRAPH" 76 130 315 18 11.5 $C.GreenDark $true)
    [void](Add-Text $slide "Score medio per batch /100" 76 158 260 19 15.5 $C.Navy $true "Aptos Display")
    Add-SummaryFidelityBar $slide "A" 93.0 196
    Add-SummaryFidelityBar $slide "B" 89.5 226
    Add-SummaryFidelityBar $slide "C1" 93.6 256
    Add-SummaryFidelityBar $slide "C2" 93.62 286
    [void](Add-Pill $slide "92,4/100 media" 76 329 128 25 $C.GreenDark $C.White 10)
    [void](Add-Pill $slide "38/38 usabili" 214 329 112 25 $C.Blue $C.White 10)
    [void](Add-Text $slide "32 VERY HIGH $middleDot 4 HIGH $middleDot 2 MEDIUM $middleDot 0 LOW" 76 367 325 14 9.5 $C.Muted $true)

    [void](Add-Card $slide 475 112 430 278 $C.White $C.Border)
    [void](Add-Text $slide "DIAGNOSI: QUANTO AGGIUNGE L'IMMAGINE?" 498 130 342 18 11.5 $C.GreenDark $true)
    [void](Add-Text $slide "Score medio /21" 498 158 180 19 15.5 $C.Navy $true "Aptos Display")
    [void](Add-Pill $slide "256 run" 817 151 64 24 $C.Navy $C.White 9.6)

    [void](Add-Card $slide 498 188 10 10 $C.Blue $C.Blue)
    [void](Add-Text $slide "JSON + datasheet" 514 185 112 15 9.3 $C.Slate $false)
    [void](Add-Card $slide 641 188 10 10 $C.Violet $C.Violet)
    [void](Add-Text $slide "JSON + immagine" 657 185 116 15 9.3 $C.Slate $false)

    Add-SummaryDiagnosticBar $slide "Batch v1" 15.672 15.938 218
    Add-SummaryDiagnosticBar $slide "Batch v2" 14.938 15.312 272

    [void](Add-Pill $slide "Delta score +0,32" 500 328 122 25 $C.Green $C.White 9.7)
    [void](Add-Pill $slide "Top-1 +3,9 pp" 632 328 111 25 $C.Blue $C.White 9.7)
    [void](Add-Pill $slide "Top-3 85,2%" 753 328 112 25 $C.Violet $C.White 9.7)
    [void](Add-Text $slide "Lo score cresce poco: il contributo visivo dipende dal circuito e dal modello." 500 367 365 14 9.4 $C.Muted $true)

    [void](Add-Card $slide 55 408 850 72 $C.GreenSoft $C.GreenLine)
    [void](Add-Text $slide "MESSAGGIO CHIAVE" 75 423 143 16 10.8 $C.GreenDark $true)
    [void](Add-Text $slide "Il Graph JSON conserva gi$agrave gran parte dell'informazione necessaria al troubleshooting. L'immagine $egrave complementare: pu$ograve aiutare, essere neutra o introdurre rumore a seconda del caso." 213 419 666 34 11.2 $C.Slate $true)
    [void](Add-Text $slide "Limite: un solo judge e una sola run per combinazione; benchmark uniforme, non validazione statistica multi-rater." 213 458 666 13 8.8 $C.Muted $false)

    Add-Notes $slide "La verifica image-graph produce una media complessiva di circa 92,4 su 100. Tutti i 38 grafi sono giudicati utilizzabili come base: 32 VERY HIGH, quattro HIGH e due MEDIUM, senza casi LOW. Nel benchmark diagnostico, aggregando i due batch, aggiungere l'immagine porta lo score medio da 15,30 a 15,63 su 21. Il miglioramento medio $egrave piccolo e non sistematico: il JSON $egrave gi$agrave informativo e l'immagine va considerata come supporto complementare."
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
$outputPath = [IO.Path]::GetFullPath($OutputPresentation)
[IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($outputPath)) | Out-Null

$backgroundAsset = Join-Path ([IO.Path]::GetDirectoryName($outputPath)) "_light_template_background.png"
Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive = [IO.Compression.ZipFile]::OpenRead($sourcePath)
try {
    # Slide 5 uses rId3 -> ppt/media/image1.png as its light template image.
    $entry = $archive.GetEntry("ppt/media/image1.png")
    if (-not $entry) { throw "Light template background not found." }
    $inputStream = $entry.Open()
    try {
        $outputStream = [IO.File]::Create($backgroundAsset)
        try { $inputStream.CopyTo($outputStream) }
        finally { $outputStream.Dispose() }
    }
    finally { $inputStream.Dispose() }
}
finally { $archive.Dispose() }

function Invoke-PowerPointPhase(
    [string]$inputPath,
    [string]$phaseOutputPath,
    [string]$phaseName,
    [scriptblock]$work
) {
    if (Test-Path -LiteralPath $phaseOutputPath) {
        Remove-Item -LiteralPath $phaseOutputPath
    }

    $powerPoint = $null
    $presentation = $null
    try {
        Write-Output "PHASE $phaseName open"
        $powerPoint = New-Object -ComObject PowerPoint.Application
        $powerPoint.Visible = -1
        $powerPoint.WindowState = 2
        $powerPoint.DisplayAlerts = 1
        $presentation = $powerPoint.Presentations.Open($inputPath, 0, 0, -1)

        & $work $presentation

        Write-Output "PHASE $phaseName save"
        $presentation.SaveCopyAs($phaseOutputPath, 24, 0)
        Write-Output "PHASE $phaseName done"
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
}

function Set-PageNumbersInPackage([string]$presentationPath) {
    Add-Type -AssemblyName System.IO.Compression
    $zip = [IO.Compression.ZipFile]::Open($presentationPath, [IO.Compression.ZipArchiveMode]::Update)
    try {
        function Read-ZipText($entry) {
            $reader = [IO.StreamReader]::new($entry.Open())
            try { return $reader.ReadToEnd() }
            finally { $reader.Dispose() }
        }

        [xml]$presentationXml = Read-ZipText ($zip.GetEntry("ppt/presentation.xml"))
        [xml]$relationshipsXml = Read-ZipText ($zip.GetEntry("ppt/_rels/presentation.xml.rels"))

        $presentationNs = [Xml.XmlNamespaceManager]::new($presentationXml.NameTable)
        $presentationNs.AddNamespace("p", "http://schemas.openxmlformats.org/presentationml/2006/main")
        $presentationNs.AddNamespace("r", "http://schemas.openxmlformats.org/officeDocument/2006/relationships")

        $relationshipMap = @{}
        foreach ($relationship in $relationshipsXml.Relationships.Relationship) {
            $relationshipMap[$relationship.Id] = $relationship.Target
        }

        $slideIds = $presentationXml.SelectNodes("//p:sldIdLst/p:sldId", $presentationNs)
        for ($index = 0; $index -lt $slideIds.Count; $index++) {
            $relationshipId = $slideIds[$index].GetAttribute("id", "http://schemas.openxmlformats.org/officeDocument/2006/relationships")
            $target = $relationshipMap[$relationshipId]
            if (-not $target) { continue }
            $entryName = "ppt/" + $target.TrimStart("/")
            $entry = $zip.GetEntry($entryName)
            if (-not $entry) { continue }

            [xml]$slideXml = Read-ZipText $entry
            $slideXml.PreserveWhitespace = $true
            $slideNs = [Xml.XmlNamespaceManager]::new($slideXml.NameTable)
            $slideNs.AddNamespace("p", "http://schemas.openxmlformats.org/presentationml/2006/main")
            $slideNs.AddNamespace("a", "http://schemas.openxmlformats.org/drawingml/2006/main")

            $updated = $false
            foreach ($shape in $slideXml.SelectNodes("//p:sp", $slideNs)) {
                $offset = $shape.SelectSingleNode("p:spPr/a:xfrm/a:off", $slideNs)
                $textNode = $shape.SelectSingleNode("p:txBody/a:p/a:r/a:t", $slideNs)
                if (-not $offset -or -not $textNode) { continue }
                $x = [long]$offset.GetAttribute("x")
                $y = [long]$offset.GetAttribute("y")
                if ($x -ge 10500000 -and $y -ge 6000000) {
                    $textNode.InnerText = "{0:D2}" -f ($index + 1)
                    $updated = $true
                }
            }

            if ($updated) {
                $stream = $entry.Open()
                try {
                    $stream.SetLength(0)
                    $settings = [Xml.XmlWriterSettings]::new()
                    $settings.Encoding = [Text.UTF8Encoding]::new($false)
                    $settings.OmitXmlDeclaration = $false
                    $writer = [Xml.XmlWriter]::Create($stream, $settings)
                    try { $slideXml.Save($writer) }
                    finally { $writer.Dispose() }
                }
                finally { $stream.Dispose() }
            }
        }
    }
    finally { $zip.Dispose() }
}

$stage1Path = [IO.Path]::Combine([IO.Path]::GetDirectoryName($outputPath), "_stage_results_1.pptx")
$stage2Path = [IO.Path]::Combine([IO.Path]::GetDirectoryName($outputPath), "_stage_results_2.pptx")

Invoke-PowerPointPhase $sourcePath $stage1Path "1_experiment" {
    param($presentation)
    $slide5 = $presentation.Slides.Add(5, 12)
    Add-LightTemplateSkeleton $slide5 $backgroundAsset
    $slide6 = $presentation.Slides.Add(6, 12)
    Add-LightTemplateSkeleton $slide6 $backgroundAsset
    Build-ExperimentSlide $slide5
}

Invoke-PowerPointPhase $stage1Path $stage2Path "2_model_results" {
    param($presentation)
    Build-ModelResultsSlide $presentation.Slides.Item(6)
}

Invoke-PowerPointPhase $stage2Path $outputPath "3_verification_summary" {
    param($presentation)
    Build-VerificationSummarySlide $presentation.Slides.Item(8)
}

Write-Output "PHASE 4_page_numbers"
Set-PageNumbersInPackage $outputPath

foreach ($temporaryPath in @($stage1Path, $stage2Path)) {
    if (Test-Path -LiteralPath $temporaryPath) {
        Remove-Item -LiteralPath $temporaryPath
    }
}

Write-Output "Saved=$outputPath"
Write-Output "Slides=14"
