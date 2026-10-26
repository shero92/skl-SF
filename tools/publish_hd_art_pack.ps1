# Owner-approved ONE-TIME real-PNG import and push. Coding agents do not generate images.
param(
    [string]$ZipPath = "$HOME\Downloads\hero_room_hd_factory_pack_2026-10-26.zip"
)
$ErrorActionPreference = 'Stop'
function Run-Git {
    & git @args
    if ($LASTEXITCODE -ne 0) { throw "Git command failed: git $args" }
}
function Run-Python {
    & py -3 @args
    if ($LASTEXITCODE -ne 0) { throw "Python command failed: py -3 $args" }
}
if (-not (Test-Path -LiteralPath $ZipPath -PathType Leaf)) {
    throw "The real ChatGPT art ZIP was not found: $ZipPath"
}
if (-not (Test-Path 'project.godot') -or -not (Test-Path 'tools/map_factory_cli.py')) {
    throw "Run this script from the skl-SF repository root"
}
$changes = & git status --porcelain
if ($LASTEXITCODE -ne 0) { throw "Cannot read git status" }
if ($changes) { throw "Please commit/stash other changes first. No overwrite allowed." }
Run-Git switch main
Run-Git fetch origin main
Run-Git merge --ff-only origin/main
$branch = "art/hero-room-hd-pngs-20261026"
Run-Git switch -c $branch
Run-Python tools/install_hd_factory_pack.py $ZipPath
Run-Python tools/install_hd_factory_pack.py $ZipPath --install --integrate
Run-Python tools/map_factory_cli.py validate
Run-Python tools/run_tests.py --changed
# Run Godot if installed: validate real native resources, sprite imports and placement.
$engine = Get-Command godot -ErrorAction SilentlyContinue
if (-not $engine) { $engine = Get-Command godot4 -ErrorAction SilentlyContinue }
if ($engine) {
    & $engine.Source --headless --path . --editor --quit
    if ($LASTEXITCODE -ne 0) { throw "Godot import failed; changes remain local for repair" }
    & $engine.Source --headless --path . --script res://tools/map_factory_godot_smoke.gd
    if ($LASTEXITCODE -ne 0) { throw "Godot map smoke failed; changes remain local for repair" }
} else {
    Write-Warning "Godot not in PATH; GitHub Actions will check it after push"
}
# A clean checkout was required, and only the intended paths are staged.
Run-Git add map_factory/parts map_factory/metadata/asset_index.json map_factory/maps/hero_room_01 map_factory/maps/index.json
Run-Git commit -m "art: import nine genuine ChatGPT HD sprites into Hero Room"
Run-Git push -u origin $branch
Write-Host "SUCCESS! Genuine PNGs are now uploaded to GitHub branch $branch"
Write-Host "Open a PR for the branch; only after Godot visual approval should it become the production quality default."
