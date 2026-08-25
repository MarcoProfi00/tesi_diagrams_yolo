param(
    [Parameter(Mandatory = $true)]
    [string]$OutputPresentation
)

$ErrorActionPreference = "Stop"

$requestedOutput = $OutputPresentation
$libraryPath = Join-Path $PSScriptRoot "revise_diagnostic_results_slides.ps1"
. $libraryPath -LibraryOnly
$OutputPresentation = $requestedOutput

$workspaceRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$outputPath = [IO.Path]::GetFullPath($OutputPresentation)
$outputDirectory = [IO.Path]::GetDirectoryName($outputPath)
[IO.Directory]::CreateDirectory($outputDirectory) | Out-Null

$basePresentation = Join-Path $workspaceRoot "outputs\presentations\tesi_object_detection_diagnosi_ai_risultati_gpt_finale.pptx"
$pipeline1OutputRoot = Join-Path $workspaceRoot "outputs\demo_workspaces\demo_b03\pipeline1.0"
$imagePaths = @(
    (Join-Path $pipeline1OutputRoot "02_assign_instances\debug_images\b02_instances.jpg"),
    (Join-Path $pipeline1OutputRoot "03_estimate_terminals\debug_images\b02_terminals.jpg"),
    (Join-Path $pipeline1OutputRoot "04_extract_wires\skeleton\b02_skeleton.png"),
    (Join-Path $pipeline1OutputRoot "05_build_terminal_graph\debug_terminal_overlay\b02_terminal_overlay.jpg")
)

foreach ($path in @($basePresentation) + $imagePaths) {
    if (-not (Test-Path -LiteralPath $path)) { throw "Required file not found: $path" }
}

function Add-PhaseCard(
    $slide,
    [double]$left,
    [string]$number,
    [string]$title,
    [string]$caption,
    [int]$accentColor
) {
    [void](Add-Card $slide $left 116 205 363 $C.White $C.Border)

    $accent = $slide.Shapes.AddShape(1, $left, 116, 205, 5)
    Set-ShapeFill $accent $accentColor
    Set-ShapeLine $accent $accentColor 0 $false

    [void](Add-Pill $slide $number ($left + 12) 133 34 22 $accentColor $C.White 9.2)
    [void](Add-Text $slide $title ($left + 55) 135 137 18 10.6 $C.Navy $true "Aptos")

    $imageFrame = $slide.Shapes.AddShape(1, ($left + 9), 166, 187, 187)
    Set-ShapeFill $imageFrame $C.White
    Set-ShapeLine $imageFrame $C.BorderSoft 1 $true

    [void](Add-Text $slide $caption ($left + 13) 369 179 34 9.7 $C.Slate $true "Aptos" 2)

    $captionRule = $slide.Shapes.AddLine(($left + 31), 414, ($left + 174), 414)
    $captionRule.Line.ForeColor.RGB = $C.BorderSoft
    $captionRule.Line.Weight = 0.8
    [void](Add-Text $slide "output reale  |  demo b02" ($left + 18) 430 169 14 8.2 $C.Muted $false "Aptos" 2)
}

function Invoke-PowerPointPhase(
    [string]$inputPath,
    [string]$phaseOutputPath,
    [scriptblock]$work
) {
    if (Test-Path -LiteralPath $phaseOutputPath) { Remove-Item -LiteralPath $phaseOutputPath }
    $powerPoint = $null
    $presentation = $null
    try {
        $powerPoint = New-Object -ComObject PowerPoint.Application
        $powerPoint.Visible = -1
        $powerPoint.WindowState = 2
        $powerPoint.DisplayAlerts = 1
        $presentation = $powerPoint.Presentations.Open($inputPath, 0, 0, -1)
        & $work $presentation
        $presentation.SaveCopyAs($phaseOutputPath, 24, 0)
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

function Keep-OnlySlide(
    [string]$sourcePath,
    [int]$slideIndex,
    [string]$finalPath
) {
    Copy-Item -LiteralPath $sourcePath -Destination $finalPath -Force
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    Add-Type -AssemblyName System.IO.Compression

    function Read-ZipText($entry) {
        $reader = [IO.StreamReader]::new($entry.Open())
        try { return $reader.ReadToEnd() }
        finally { $reader.Dispose() }
    }

    function Write-ZipXml($entry, [xml]$document) {
        $stream = $entry.Open()
        try {
            $stream.SetLength(0)
            $settings = [Xml.XmlWriterSettings]::new()
            $settings.Encoding = [Text.UTF8Encoding]::new($false)
            $settings.OmitXmlDeclaration = $false
            $writer = [Xml.XmlWriter]::Create($stream, $settings)
            try { $document.Save($writer) }
            finally { $writer.Dispose() }
        }
        finally { $stream.Dispose() }
    }

    $zip = [IO.Compression.ZipFile]::Open($finalPath, [IO.Compression.ZipArchiveMode]::Update)
    try {
        $presentationEntry = $zip.GetEntry("ppt/presentation.xml")
        [xml]$presentationXml = Read-ZipText $presentationEntry
        $presentationXml.PreserveWhitespace = $true
        $ns = [Xml.XmlNamespaceManager]::new($presentationXml.NameTable)
        $ns.AddNamespace("p", "http://schemas.openxmlformats.org/presentationml/2006/main")
        $slideList = $presentationXml.SelectSingleNode("//p:sldIdLst", $ns)
        $slideIds = @($presentationXml.SelectNodes("//p:sldIdLst/p:sldId", $ns))
        if ($slideIndex -lt 1 -or $slideIndex -gt $slideIds.Count) { throw "Slide index out of range." }
        $keepNode = $slideIds[$slideIndex - 1]
        foreach ($node in $slideIds) {
            if (-not [object]::ReferenceEquals($node, $keepNode)) { [void]$slideList.RemoveChild($node) }
        }
        Write-ZipXml $presentationEntry $presentationXml

        $appEntry = $zip.GetEntry("docProps/app.xml")
        if ($appEntry) {
            [xml]$appXml = Read-ZipText $appEntry
            $appXml.PreserveWhitespace = $true
            $appNs = [Xml.XmlNamespaceManager]::new($appXml.NameTable)
            $appNs.AddNamespace("ep", "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties")
            $slidesNode = $appXml.SelectSingleNode("//ep:Slides", $appNs)
            if ($slidesNode) { $slidesNode.InnerText = "1" }
            Write-ZipXml $appEntry $appXml
        }
    }
    finally { $zip.Dispose() }
}

function Add-ImagesToSlidePackage(
    [string]$sourcePath,
    [int]$slidePartNumber,
    [string]$targetPath
) {
    Copy-Item -LiteralPath $sourcePath -Destination $targetPath -Force
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    Add-Type -AssemblyName System.IO.Compression

    function Read-PackageText($entry) {
        $reader = [IO.StreamReader]::new($entry.Open())
        try { return $reader.ReadToEnd() }
        finally { $reader.Dispose() }
    }

    function Write-PackageXml($entry, [xml]$document) {
        $stream = $entry.Open()
        try {
            $stream.SetLength(0)
            $settings = [Xml.XmlWriterSettings]::new()
            $settings.Encoding = [Text.UTF8Encoding]::new($false)
            $settings.OmitXmlDeclaration = $false
            $writer = [Xml.XmlWriter]::Create($stream, $settings)
            try { $document.Save($writer) }
            finally { $writer.Dispose() }
        }
        finally { $stream.Dispose() }
    }

    $zip = [IO.Compression.ZipFile]::Open($targetPath, [IO.Compression.ZipArchiveMode]::Update)
    try {
        $slideEntry = $zip.GetEntry("ppt/slides/slide$slidePartNumber.xml")
        $relsEntry = $zip.GetEntry("ppt/slides/_rels/slide$slidePartNumber.xml.rels")
        if (-not $slideEntry -or -not $relsEntry) { throw "Target slide package parts not found." }

        [xml]$slideXml = Read-PackageText $slideEntry
        $slideXml.PreserveWhitespace = $true
        [xml]$relsXml = Read-PackageText $relsEntry
        $relsXml.PreserveWhitespace = $true

        $ns = [Xml.XmlNamespaceManager]::new($slideXml.NameTable)
        $ns.AddNamespace("p", "http://schemas.openxmlformats.org/presentationml/2006/main")
        $ns.AddNamespace("a", "http://schemas.openxmlformats.org/drawingml/2006/main")
        $shapeTree = $slideXml.SelectSingleNode("//p:spTree", $ns)

        $maxShapeId = 1
        foreach ($node in $slideXml.SelectNodes("//p:cNvPr", $ns)) {
            $shapeId = 0
            if ([int]::TryParse($node.GetAttribute("id"), [ref]$shapeId) -and $shapeId -gt $maxShapeId) {
                $maxShapeId = $shapeId
            }
        }

        $maxRelationshipId = 0
        foreach ($relationship in $relsXml.Relationships.Relationship) {
            if ($relationship.Id -match '^rId(\d+)$') {
                $number = [int]$Matches[1]
                if ($number -gt $maxRelationshipId) { $maxRelationshipId = $number }
            }
        }

        $leftPositions = @(54, 276, 498, 720)
        $phaseNumbers = @("02", "03", "04", "05")
        for ($index = 0; $index -lt $imagePaths.Count; $index++) {
            $extension = [IO.Path]::GetExtension($imagePaths[$index]).ToLowerInvariant()
            $mediaFileName = "pipeline1_phase_$($phaseNumbers[$index])$extension"
            $mediaEntryName = "ppt/media/$mediaFileName"
            $existingMedia = $zip.GetEntry($mediaEntryName)
            if ($existingMedia) { $existingMedia.Delete() }
            $mediaEntry = $zip.CreateEntry($mediaEntryName, [IO.Compression.CompressionLevel]::Optimal)
            $inputStream = [IO.File]::OpenRead($imagePaths[$index])
            try {
                $outputStream = $mediaEntry.Open()
                try { $inputStream.CopyTo($outputStream) }
                finally { $outputStream.Dispose() }
            }
            finally { $inputStream.Dispose() }

            $maxRelationshipId++
            $relationshipId = "rId$maxRelationshipId"
            $relationship = $relsXml.CreateElement("Relationship", "http://schemas.openxmlformats.org/package/2006/relationships")
            $relationship.SetAttribute("Id", $relationshipId)
            $relationship.SetAttribute("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
            $relationship.SetAttribute("Target", "../media/$mediaFileName")
            [void]$relsXml.DocumentElement.AppendChild($relationship)

            $maxShapeId++
            $x = [long]($leftPositions[$index] * 12700)
            $y = [long](167 * 12700)
            $width = [long](187 * 12700)
            $height = [long](187 * 12700)
            $pictureXml = @"
<root xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <p:pic>
    <p:nvPicPr>
      <p:cNvPr id="$maxShapeId" name="Pipeline output phase $($phaseNumbers[$index])" descr="$mediaFileName"/>
      <p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr>
      <p:nvPr/>
    </p:nvPicPr>
    <p:blipFill>
      <a:blip r:embed="$relationshipId"/>
      <a:stretch><a:fillRect/></a:stretch>
    </p:blipFill>
    <p:spPr>
      <a:xfrm><a:off x="$x" y="$y"/><a:ext cx="$width" cy="$height"/></a:xfrm>
      <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
      <a:ln w="11430"><a:solidFill><a:srgbClr val="E2E8F0"/></a:solidFill></a:ln>
    </p:spPr>
  </p:pic>
</root>
"@
            [xml]$temporaryXml = $pictureXml
            $pictureNode = $slideXml.ImportNode($temporaryXml.DocumentElement.FirstChild, $true)
            [void]$shapeTree.AppendChild($pictureNode)
        }

        Write-PackageXml $slideEntry $slideXml
        Write-PackageXml $relsEntry $relsXml

        $contentTypesEntry = $zip.GetEntry("[Content_Types].xml")
        [xml]$contentTypesXml = Read-PackageText $contentTypesEntry
        $contentTypesXml.PreserveWhitespace = $true
        $jpegDefault = $contentTypesXml.Types.Default | Where-Object { $_.Extension -in @("jpg", "jpeg") }
        if (-not $jpegDefault) {
            $defaultNode = $contentTypesXml.CreateElement("Default", "http://schemas.openxmlformats.org/package/2006/content-types")
            $defaultNode.SetAttribute("Extension", "jpg")
            $defaultNode.SetAttribute("ContentType", "image/jpeg")
            [void]$contentTypesXml.DocumentElement.PrependChild($defaultNode)
            Write-PackageXml $contentTypesEntry $contentTypesXml
        }
    }
    finally { $zip.Dispose() }
}

$stageLayout = Join-Path $outputDirectory "_stage_pipeline1_outputs_layout.pptx"
$stageImages = Join-Path $outputDirectory "_stage_pipeline1_outputs_images.pptx"
foreach ($path in @($stageLayout, $stageImages, $outputPath)) {
    if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path }
}

Write-Output "PHASE layout"
Invoke-PowerPointPhase $basePresentation $stageLayout {
    param($presentation)
    $slide = $presentation.Slides.Item(5)
    Clear-SlideBody $slide
    Set-SlideHeader $slide "Pipeline 1.0: output intermedi" "Lo stesso circuito attraverso le fasi di ricostruzione del Graph JSON"

    Add-PhaseCard $slide 45  "02" "Istanze univoche"  "ID univoco per ogni componente"       $C.Blue
    Add-PhaseCard $slide 267 "03" "Terminali stimati" "Pin e polarit$agrave localizzati"      $C.Violet
    Add-PhaseCard $slide 489 "04" "Fili estratti"      "Scheletro dei collegamenti estratti" $C.Green
    Add-PhaseCard $slide 711 "05" "Overlay terminali"  "Terminali associati al grafo"        $C.Navy

    foreach ($shape in $slide.Shapes) {
        if ($shape.HasTextFrame -eq -1 -and $shape.Top -ge 500 -and $shape.Left -lt 500) {
            $shape.TextFrame.TextRange.Text = "Pipeline 1.0  |  output intermedi"
        }
        elseif ($shape.HasTextFrame -eq -1 -and $shape.Top -ge 485 -and $shape.Left -ge 850) {
            $shape.TextFrame.TextRange.Text = "XX"
        }
    }
}

Write-Output "PHASE embed_images"
Add-ImagesToSlidePackage $stageLayout 5 $stageImages

Write-Output "PHASE extract_single_slide"
Keep-OnlySlide $stageImages 5 $outputPath

foreach ($path in @($stageLayout, $stageImages)) {
    if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path }
}

Write-Output "Saved=$outputPath"
