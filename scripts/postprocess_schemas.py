#!/usr/bin/env python3
"""Post-process the EDI schemas emitted by `bal edi convertEdifactSchema`.

Run this after every regeneration, before `bal edi libgen`. It repairs two
defects in the converter output that otherwise make the generated libraries
fail to compile:

1. Illegal identifiers. Element names become Ballerina record field names, but
   the converter does not strip every character that is illegal in an
   identifier -- "United Nations Dangerous Goods (UNDG) identifier" keeps its
   parentheses, which is a syntax error in 43 of the D03A schemas.

2. Missing service segment definitions. UGH and UGT (the anti-collision segment
   group header/trailer) are referenced by PAYDUC and JUPREQ but live in the
   ISO 9735 service segment directory, not in the message directory the
   converter reads, and they are not among its hardcoded service segments.
   libgen fails with "Segement reference not found. Reference: UGH".
   Definitions below follow the UN/EDIFACT service segment specification
   (syntax version 4): a single mandatory element 0087, an..4.
   https://service.unece.org/trade/untdid/d03a/trsd/trsdugh.htm

3. Colliding sibling segment tags. When a message repeats the same segment at
   two positions of the same segment group, the converter gives both entries the
   same tag, and codegen then emits two record fields with that name
   ("redeclared symbol 'Free_text'"). Duplicates are suffixed "_1", "_2", ...,
   the same convention the converter already uses for repeated fields.

Usage: python3 scripts/postprocess_schemas.py [schema-root]
"""
import collections
import json
import pathlib
import re
import sys

IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
ILLEGAL = re.compile(r"[^A-Za-z0-9_]")

SERVICE_SEGMENTS = {
    "UGH": {
        "code": "UGH",
        "tag": "Anti_collision_segment_group_header",
        "fields": [
            {"tag": "code", "required": True, "repeat": False},
            {
                "tag": "ANTI_COLLISION_SEGMENT_GROUP_IDENTIFICATION",
                "dataType": "string",
                "required": True,
                "repeat": False,
            },
        ],
    },
    "UGT": {
        "code": "UGT",
        "tag": "Anti_collision_segment_group_trailer",
        "fields": [
            {"tag": "code", "required": True, "repeat": False},
            {
                "tag": "ANTI_COLLISION_SEGMENT_GROUP_IDENTIFICATION",
                "dataType": "string",
                "required": True,
                "repeat": False,
            },
        ],
    },
}


def sanitize(tag):
    cleaned = re.sub(r"_+", "_", ILLEGAL.sub("", tag)).strip("_")
    return cleaned if IDENTIFIER.match(cleaned) else "_" + cleaned


def fix_tags(node):
    fixed = 0
    if isinstance(node, dict):
        tag = node.get("tag")
        if isinstance(tag, str) and not IDENTIFIER.match(tag):
            node["tag"] = sanitize(tag)
            fixed += 1
        for value in node.values():
            fixed += fix_tags(value)
    elif isinstance(node, list):
        for value in node:
            fixed += fix_tags(value)
    return fixed


def referenced(node, order):
    """Collect segment refs in first-appearance order."""
    if isinstance(node, dict):
        ref = node.get("ref")
        if isinstance(ref, str) and ref not in order:
            order.append(ref)
        for value in node.values():
            referenced(value, order)
    elif isinstance(node, list):
        for value in node:
            referenced(value, order)
    return order


def add_missing_segments(schema):
    definitions = schema.get("segmentDefinitions")
    if definitions is None:
        return 0
    order = referenced(schema.get("segments"), [])
    missing = [ref for ref in order if ref not in definitions]
    if not missing:
        return 0
    unknown = [ref for ref in missing if ref not in SERVICE_SEGMENTS]
    if unknown:
        raise SystemExit(f"error: no definition available for segment(s) {unknown}")
    # Insert each entry where the converter would have emitted it -- right after
    # the definition of the segment that precedes it in the segment table --
    # instead of rebuilding, so the existing key order is preserved. The
    # envelope segments are not in `order`, having been lifted out of
    # `segments`, and would otherwise be pushed to the end.
    for ref in missing:
        preceding = order[:order.index(ref)]
        after = next((seen for seen in reversed(preceding) if seen in definitions), None)
        rebuilt = collections.OrderedDict()
        if after is None:
            rebuilt[ref] = SERVICE_SEGMENTS[ref]
        for key, definition in definitions.items():
            rebuilt[key] = definition
            if key == after:
                rebuilt[ref] = SERVICE_SEGMENTS[ref]
        definitions = rebuilt
    schema["segmentDefinitions"] = definitions
    return len(missing)


def dedupe_sibling_tags(seglist):
    renamed = 0
    if not isinstance(seglist, list):
        return renamed
    seen = collections.Counter()
    for segment in seglist:
        if not isinstance(segment, dict):
            continue
        tag = segment.get("tag")
        if isinstance(tag, str):
            seen[tag] += 1
            if seen[tag] > 1:
                segment["tag"] = f"{tag}_{seen[tag] - 1}"
                renamed += 1
        renamed += dedupe_sibling_tags(segment.get("segments"))
    return renamed


def main():
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "d03a")
    tags = segments = collisions = files = 0
    for path in sorted(root.glob("*/*.json")):
        schema = json.loads(path.read_text(encoding="utf-8"),
                            object_pairs_hook=collections.OrderedDict)
        fixed_tags = fix_tags(schema)
        added_segments = add_missing_segments(schema)
        renamed = dedupe_sibling_tags(schema.get("segments"))
        if fixed_tags or added_segments or renamed:
            tags += fixed_tags
            segments += added_segments
            collisions += renamed
            files += 1
            # Match the converter's own formatting so a regen produces no
            # spurious whitespace diff.
            path.write_text(
                json.dumps(schema, separators=(", ", ":"), ensure_ascii=False),
                encoding="utf-8")
    print(f"post-processed {files} file(s): {tags} illegal tag(s), "
          f"{segments} missing segment definition(s), "
          f"{collisions} colliding sibling tag(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
