extends RefCounted
class_name AssetCatalog

var _records: Dictionary = {}

func load_index(path: String = "res://map_factory/metadata/asset_index.json") -> bool:
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
