param(
    [Parameter(Mandatory = $true)]
    [string]$SourcePresentation,

    [Parameter(Mandatory = $true)]
    [string]$OutputPresentation
)

$ErrorActionPreference = "Stop"

$sourcePath = (Resolve-Path -LiteralPath $SourcePresentation).Path
$outputPath = [IO.Path]::GetFullPath($OutputPresentation)
[IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($outputPath)) | Out-Null

if (-not [string]::Equals($sourcePath, $outputPath, [StringComparison]::OrdinalIgnoreCase)) {
    Copy-Item -LiteralPath $sourcePath -Destination $outputPath -Force
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.IO.Compression

function Read-EntryText($entry) {
    $reader = [IO.StreamReader]::new($entry.Open())
    try { return $reader.ReadToEnd() }
    finally { $reader.Dispose() }
}

function Write-EntryXml($entry, [xml]$document) {
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

$zip = [IO.Compression.ZipFile]::Open($outputPath, [IO.Compression.ZipArchiveMode]::Update)
try {
    $sourceSlideEntry = $zip.GetEntry("ppt/slides/slide7.xml")
    if (-not $sourceSlideEntry) { throw "Template slide part slide7.xml not found." }
    [xml]$sourceSlideXml = Read-EntryText $sourceSlideEntry
    $sourceNs = [Xml.XmlNamespaceManager]::new($sourceSlideXml.NameTable)
    $sourceNs.AddNamespace("p", "http://schemas.openxmlformats.org/presentationml/2006/main")
    $sourceNs.AddNamespace("a", "http://schemas.openxmlformats.org/drawingml/2006/main")
    $sourceNs.AddNamespace("r", "http://schemas.openxmlformats.org/officeDocument/2006/relationships")
    $backgroundPicture = $sourceSlideXml.SelectSingleNode("//p:spTree/p:pic[p:nvPicPr/p:cNvPr[@descr='light_circuit_template_bg.png']]", $sourceNs)
    if (-not $backgroundPicture) { throw "Light template picture not found on slide 7." }

    foreach ($slideNumber in @(5, 6)) {
        $slideEntry = $zip.GetEntry("ppt/slides/slide$slideNumber.xml")
        $relsEntry = $zip.GetEntry("ppt/slides/_rels/slide$slideNumber.xml.rels")
        if (-not $slideEntry -or -not $relsEntry) { throw "Slide $slideNumber package parts are missing." }

        [xml]$slideXml = Read-EntryText $slideEntry
        $slideXml.PreserveWhitespace = $true
        $ns = [Xml.XmlNamespaceManager]::new($slideXml.NameTable)
        $ns.AddNamespace("p", "http://schemas.openxmlformats.org/presentationml/2006/main")
        $ns.AddNamespace("a", "http://schemas.openxmlformats.org/drawingml/2006/main")
        $ns.AddNamespace("r", "http://schemas.openxmlformats.org/officeDocument/2006/relationships")

        $shapeTree = $slideXml.SelectSingleNode("//p:spTree", $ns)
        $canvas = $null
        foreach ($shape in $slideXml.SelectNodes("//p:spTree/p:sp", $ns)) {
            $offset = $shape.SelectSingleNode("p:spPr/a:xfrm/a:off", $ns)
            $extent = $shape.SelectSingleNode("p:spPr/a:xfrm/a:ext", $ns)
            if ($offset -and $extent -and
                [long]$offset.GetAttribute("x") -eq 0 -and [long]$offset.GetAttribute("y") -eq 0 -and
                [long]$extent.GetAttribute("cx") -ge 12190000 -and [long]$extent.GetAttribute("cy") -ge 6857000) {
                $canvas = $shape
                break
            }
        }
        if ($canvas) { [void]$shapeTree.RemoveChild($canvas) }

        $maxId = 1
        foreach ($node in $slideXml.SelectNodes("//p:cNvPr", $ns)) {
            $value = 0
            if ([int]::TryParse($node.GetAttribute("id"), [ref]$value) -and $value -gt $maxId) { $maxId = $value }
        }

        $picture = $slideXml.ImportNode($backgroundPicture, $true)
        $picture.SelectSingleNode("p:nvPicPr/p:cNvPr", $ns).SetAttribute("id", [string]($maxId + 1))
        $picture.SelectSingleNode("p:nvPicPr/p:cNvPr", $ns).SetAttribute("name", "Light template background")
        $picture.SelectSingleNode("p:blipFill/a:blip", $ns).SetAttribute("embed", "http://schemas.openxmlformats.org/officeDocument/2006/relationships", "rId3")

        $groupProperties = $shapeTree.SelectSingleNode("p:grpSpPr", $ns)
        if ($groupProperties.NextSibling) {
            [void]$shapeTree.InsertBefore($picture, $groupProperties.NextSibling)
        }
        else {
            [void]$shapeTree.AppendChild($picture)
        }

        [xml]$relsXml = Read-EntryText $relsEntry
        $existing = $relsXml.Relationships.Relationship | Where-Object { $_.Id -eq "rId3" }
        if (-not $existing) {
            $relationship = $relsXml.CreateElement("Relationship", "http://schemas.openxmlformats.org/package/2006/relationships")
            $relationship.SetAttribute("Id", "rId3")
            $relationship.SetAttribute("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
            $relationship.SetAttribute("Target", "../media/image1.png")
            [void]$relsXml.DocumentElement.AppendChild($relationship)
        }

        Write-EntryXml $slideEntry $slideXml
        Write-EntryXml $relsEntry $relsXml
    }
}
finally { $zip.Dispose() }

Write-Output "Saved=$outputPath"
