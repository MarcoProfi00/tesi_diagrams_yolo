param(
    [Parameter(Mandatory = $true)]
    [string]$InputPresentation,

    [Parameter(Mandatory = $true)]
    [string]$OutputPresentation
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$inputPath = (Resolve-Path -LiteralPath $InputPresentation).Path
$outputPath = [System.IO.Path]::GetFullPath($OutputPresentation)
[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($outputPath)) | Out-Null

$utf8 = New-Object System.Text.UTF8Encoding($false)
$sourceArchive = [System.IO.Compression.ZipFile]::OpenRead($inputPath)
$outputStream = [System.IO.File]::Create($outputPath)
$targetArchive = New-Object System.IO.Compression.ZipArchive(
    $outputStream,
    [System.IO.Compression.ZipArchiveMode]::Create,
    $false
)

try {
    foreach ($sourceEntry in $sourceArchive.Entries) {
        if ([string]::IsNullOrEmpty($sourceEntry.Name)) {
            continue
        }

        $targetEntry = $targetArchive.CreateEntry(
            $sourceEntry.FullName,
            [System.IO.Compression.CompressionLevel]::Optimal
        )
        $targetEntry.LastWriteTime = $sourceEntry.LastWriteTime

        $sourceEntryStream = $sourceEntry.Open()
        $targetEntryStream = $targetEntry.Open()
        try {
            if ($sourceEntry.FullName -in @(
                "ppt/slides/_rels/slide5.xml.rels",
                "ppt/slides/_rels/slide6.xml.rels"
            )) {
                $reader = New-Object System.IO.StreamReader($sourceEntryStream, $utf8, $true)
                try {
                    [xml]$xml = $reader.ReadToEnd()
                }
                finally {
                    $reader.Dispose()
                }

                $namespaceManager = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
                $namespaceManager.AddNamespace(
                    "rel",
                    "http://schemas.openxmlformats.org/package/2006/relationships"
                )
                $imageRelationship = $xml.SelectSingleNode(
                    "//rel:Relationship[@Id='rId3']",
                    $namespaceManager
                )
                if (-not $imageRelationship) {
                    throw "Image relationship rId3 missing in $($sourceEntry.FullName)."
                }
                $imageRelationship.SetAttribute("Target", "../media/image1.png")

                $writer = New-Object System.IO.StreamWriter($targetEntryStream, $utf8)
                try {
                    $writer.Write($xml.OuterXml)
                    $writer.Flush()
                }
                finally {
                    $writer.Dispose()
                }
            }
            elseif ($sourceEntry.FullName -eq "ppt/slides/slide14.xml") {
                $reader = New-Object System.IO.StreamReader($sourceEntryStream, $utf8, $true)
                try {
                    [xml]$xml = $reader.ReadToEnd()
                }
                finally {
                    $reader.Dispose()
                }

                $namespaceManager = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
                $namespaceManager.AddNamespace(
                    "p",
                    "http://schemas.openxmlformats.org/presentationml/2006/main"
                )
                $namespaceManager.AddNamespace(
                    "a",
                    "http://schemas.openxmlformats.org/drawingml/2006/main"
                )
                $pageNumber = $xml.SelectSingleNode(
                    "//p:sp[p:nvSpPr/p:cNvPr[@name='Text 19']]//a:t",
                    $namespaceManager
                )
                if (-not $pageNumber) {
                    throw "Final page number text box not found."
                }
                $pageNumber.InnerText = "14"

                $writer = New-Object System.IO.StreamWriter($targetEntryStream, $utf8)
                try {
                    $writer.Write($xml.OuterXml)
                    $writer.Flush()
                }
                finally {
                    $writer.Dispose()
                }
            }
            else {
                $sourceEntryStream.CopyTo($targetEntryStream)
            }
        }
        finally {
            $targetEntryStream.Dispose()
            $sourceEntryStream.Dispose()
        }
    }
}
finally {
    $targetArchive.Dispose()
    $outputStream.Dispose()
    $sourceArchive.Dispose()
}

Write-Output "Repaired=$outputPath"
