extends RefCounted
class_name AssetCatalog

var _records: Dictionary = {}
static var _shared: AssetCatalog
static var load_count: int = 0 # how many times asset_index.json was parsed (measurable in tests)

## One parsed catalog for gameplay scripts. Re-parsing the whole index for every animation change was a
## per-frame-state cost in HeroPlayer; call reload() after the index file changes on disk.
static func shared() -> AssetCatalog:
    if _shared == null:
        var catalog := AssetCatalog.new()
        if not catalog.load_index():
            return catalog # not cached, so a later call can try again
        _shared = catalog
    return _shared

static func reload() -> void:
    _shared = null

func load_index(path: String = "res://map_factory/metadata/asset_index.json") -> bool:
    load_count += 1
    _records.clear()
    if not FileAccess.file_exists(path):
        push_error("Asset index missing: " + path)
        return false
    var raw: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
    if typeof(raw) != TYPE_DICTIONARY or not raw.has("assets"):
        push_error("Invalid asset index")
        return false
    for item in raw["assets"]:
        if typeof(item) == TYPE_DICTIONARY and item.has("id"):
            _records[String(item["id"])] = item
    return true

func get_asset(asset_id: String) -> Dictionary:
    return _records.get(asset_id, {})

func find_by_tag(tag: String) -> Array[Dictionary]:
    var found: Array[Dictionary] = []
    for data in _records.values():
        if tag in data.get("tags", []):
            found.append(data)
    return found

func all_assets() -> Array[Dictionary]:
    var result: Array[Dictionary] = []
    for data in _records.values():
        result.append(data)
    return result
