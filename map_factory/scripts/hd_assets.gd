extends RefCounted
class_name HdAssets

## Owner HD art. assets_hd/runtime/<same file name> is aligned to the native sprite at
## HD_SCALE x size (see tools/build_hd_runtime_textures.py). Callers scale it back down.
const RUNTIME_DIR := "res://assets_hd/runtime/"

static func resolve(path: String) -> String:
    var candidate := RUNTIME_DIR + path.get_file()
    if path.begins_with("res://assets_generated/") and ResourceLoader.exists(candidate):
        return candidate
    return path

## True when the texture can be loaded: the HD runtime twin (preferred) or the original file.
## Retired low-quality originals under assets_generated/ no longer exist; their runtime twins do.
static func exists(path: String) -> bool:
    return path != "" and ResourceLoader.exists(resolve(path))
