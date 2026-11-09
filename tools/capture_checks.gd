extends RefCounted
## Checks used by the evidence capture to refuse draft or fallback rendering (TASK-0059).
## Agent: claude (Claude Code); model: Sonnet 5.5.
##
## AssetFactory draws a magenta polygon and a "<id> (draft)" label when a texture is missing.
## A capture that contains one is not evidence of a finished room, so it must fail.

const DRAFT_SUFFIX := "(draft)"
const PLACEHOLDER_COLOR := Color(0.80, 0.12, 0.65, 0.7)


static func is_draft_placeholder(node: Node) -> bool:
	if node is Label and String((node as Label).text).ends_with(DRAFT_SUFFIX):
		return true
	if node is Polygon2D and (node as Polygon2D).color.is_equal_approx(PLACEHOLDER_COLOR):
		return true
	return false


## Names of every draft placeholder under a node (for the error message).
static func find_drafts(root: Node) -> Array:
	var found: Array = []
	_scan(root, found)
	return found


static func _scan(node: Node, found: Array) -> void:
	if is_draft_placeholder(node):
		found.append(String(node.get_path()) if node.is_inside_tree() else String(node.name))
	for child in node.get_children():
		_scan(child, found)
