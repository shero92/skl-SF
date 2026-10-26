# Imports owner-approved high-detail PNG bytes. Never creates or edits graphics.
# Safe with uncommitted work, divergent local main, and commits owned by other agents.
param(
    [string]$ZipPath = "$HOME\Downloads\hero_room_hd_factory_pack_2026-10-26.zip",
    [string]$WorktreePath = "$env:TEMP\skl-SF-hero-room-hd-20261026"
)
$ErrorActionPreference = 'Stop'
function Run-Git {
    & git @args
    if ($LASTEXITCODE -ne 0) { throw "Git command failed (exit $LASTEXITCODE): git $args" }
}
function Run-Python {
    & py -3 @args
    if ($LASTEXITCODE -ne 0) { throw "Python command failed (exit $LASTEXITCODE): py -3 $args" }
}
if (-not (Test-Path -LiteralPath $ZipPath -PathType Leaf)) {
    throw "Missing exact ChatGPT art pack ZIP: $ZipPath"
}
if (-not (Test-Path -LiteralPath 'project.godot' -PathType Leaf) -or
    -not (Test-Path -LiteralPath 'tools/map_factory_cli.py' -PathType Leaf)) {
    throw "Run this script from the skl-SF repository root"
}

# DO NOT require a clean user worktree, mutate user main, stash, reset or rebase.
# Instead checkout the fetched remote main in a NEW isolated Git worktree.
$branch = "art/hero-room-hd-pngs-20261026"
$existingBranch = & git branch --list $branch
if ($LASTEXITCODE -ne 0) { throw "Unable to check local art branches" }
if ($existingBranch) {
    throw "Branch '$branch' already exists. Inspect 'git worktree list' and 'git branch -vv' first; nothing overwritten."
}
if (Test-Path -LiteralPath $WorktreePath) {
    throw "Worktree destination already exists: $WorktreePath. Inspect it before retrying; nothing overwritten."
}
Run-Git fetch origin main
Run-Git worktree add -b $branch $WorktreePath origin/main
Write-Host "Created dedicated art worktree: $WorktreePath"
Write-Host "Local main and all existing user changes/commits are untouched."

Push-Location -LiteralPath $WorktreePath
try {
    $changes = @(& git status --porcelain=v1 --untracked-files=all)
    if ($LASTEXITCODE -ne 0) { throw "Cannot read isolated worktree status" }
    if ($changes.Count -gt 0) {
        Write-Host "Unexpected changes in isolated art worktree:"
        $changes | ForEach-Object { Write-Host $_ }
        throw "Refusing to overwrite a non-clean art worktree."
    }
    Run-Python tools/install_hd_factory_pack.py $ZipPath
    Run-Python tools/install_hd_factory_pack.py $ZipPath --install --integrate
    Run-Python tools/map_factory_cli.py validate
    Run-Python tools/run_tests.py --changed --kind python

    # If installed, validate the actual Godot resources and assembled maps.
    $engine = Get-Command godot -ErrorAction SilentlyContinue
    if (-not $engine) { $engine = Get-Command godot4 -ErrorAction SilentlyContinue }
    if ($engine) {
        & $engine.Source --headless --path . --editor --quit
        if ($LASTEXITCODE -ne 0) { throw "Godot import failed; keep art worktree for repair" }
        & $engine.Source --headless --path . --script res://tools/map_factory_godot_smoke.gd
        if ($LASTEXITCODE -ne 0) { throw "Godot map smoke failed; keep art worktree for repair" }
    } else {
        Write-Warning "Godot not in PATH; run Godot and visually review on the art branch"
    }

    Run-Git add map_factory/parts map_factory/metadata/asset_index.json map_factory/maps/hero_room_01 map_factory/maps/index.json
    Run-Git commit -m "art: import nine genuine ChatGPT HD sprites into Hero Room"
    Run-Git push -u origin $branch
    Write-Host "SUCCESS! Genuine nine PNGs pushed to GitHub branch $branch"
    Write-Host "Art worktree: $WorktreePath"
    Write-Host "Production visual QA and PR merge still required."
} finally {
    Pop-Location
}
