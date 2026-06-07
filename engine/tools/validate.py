#!/usr/bin/env python3
"""KaushalForge tool — validate work/*.json against the skill schemas.

Deterministic guardrail for the AI phases (esp. weak/local models): each phase writes
JSON, this says exactly which field is wrong. Uses `jsonschema` if installed, else a
built-in shape checker covering the keywords our schemas use (type/required/properties/
items/maxLength/maxItems). Exit 0 = all conform; non-zero = errors printed per field.

  python engine/tools/validate.py                 # validate every work/*.json present
  python engine/tools/validate.py work/profile.json work/variants.json
"""
import os, sys, json, glob

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # engine/
from kf_lib import WORK, SCHEMAS

# work file basename -> schema file
SCHEMA_FOR = {
    "profile.json": "profile.schema.json",
    "variants.json": "variants.schema.json",
    "letters.json": "letters.schema.json",
    "linkedin.json": "linkedin.schema.json",
}

def _shape_errors(inst, schema, path):
    """Minimal JSON-Schema check (no deps). Returns list of 'path: message'."""
    errs = []
    t = schema.get("type")
    if t == "object":
        if not isinstance(inst, dict):
            return ["%s: expected object, got %s" % (path, type(inst).__name__)]
        for req in schema.get("required", []):
            if req not in inst:
                errs.append("%s: missing required field '%s'" % (path or "(root)", req))
        props = schema.get("properties", {})
        for k, sub in props.items():
            if k in inst:
                errs += _shape_errors(inst[k], sub, "%s.%s" % (path, k) if path else k)
    elif t == "array":
        if not isinstance(inst, list):
            return ["%s: expected array, got %s" % (path, type(inst).__name__)]
        mx = schema.get("maxItems")
        if isinstance(mx, int) and len(inst) > mx:
            errs.append("%s: %d items > maxItems %d" % (path, len(inst), mx))
        item = schema.get("items")
        if item:
            for i, el in enumerate(inst):
                errs += _shape_errors(el, item, "%s[%d]" % (path, i))
    elif t == "string":
        if not isinstance(inst, str):
            errs.append("%s: expected string, got %s" % (path, type(inst).__name__))
        else:
            mx = schema.get("maxLength")
            if isinstance(mx, int) and len(inst) > mx:
                errs.append("%s: length %d > maxLength %d" % (path, len(inst), mx))
    elif t in ("number", "integer"):
        ok = isinstance(inst, (int, float)) and not isinstance(inst, bool)
        if t == "integer":
            ok = isinstance(inst, int) and not isinstance(inst, bool)
        if not ok:
            errs.append("%s: expected %s" % (path, t))
    elif t == "boolean":
        if not isinstance(inst, bool):
            errs.append("%s: expected boolean" % path)
    return errs

def validate_file(path):
    """Return list of error strings for one work/*.json (empty = conforms)."""
    base = os.path.basename(path)
    sname = SCHEMA_FOR.get(base)
    if not sname:
        return []  # no schema for this file (e.g. targeting.json) — skip
    spath = os.path.join(SCHEMAS, sname)
    if not os.path.exists(spath):
        return []  # schema not present in this checkout — skip (env issue, not a content issue)
    try:
        inst = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        return ["%s: invalid JSON (%s)" % (base, e)]
    try:
        schema = json.load(open(spath, encoding="utf-8"))
    except Exception as e:
        return ["%s: cannot read schema %s (%s)" % (base, sname, e)]
    # the engine tolerates {"results":[...]}/{"variants":[...]}/{"letters":[...]} wrappers
    if schema.get("type") == "array" and isinstance(inst, dict):
        for wrap in ("results", "variants", "letters"):
            if isinstance(inst.get(wrap), list):
                inst = inst[wrap]; break
    try:
        import jsonschema
        errs = ["%s -> %s" % ("/".join(str(p) for p in e.path) or "(root)", e.message)
                for e in jsonschema.Draft202012Validator(schema).iter_errors(inst)]
    except ImportError:
        errs = _shape_errors(inst, schema, "")
    return ["%s: %s" % (base, e) for e in errs]

def validate_work(files=None):
    """Validate the given files, or every known work/*.json present. List of errors."""
    if files is None:
        files = [os.path.join(WORK, b) for b in SCHEMA_FOR if os.path.exists(os.path.join(WORK, b))]
    errs = []
    for f in files:
        errs += validate_file(f)
    return errs

def main():
    args = sys.argv[1:]
    errs = validate_work(args or None)
    if errs:
        print("VALIDATE FAILED (%d):" % len(errs))
        for e in errs:
            print("  -", e)
        sys.exit(1)
    print("VALIDATE OK — work JSON conforms to schemas.")

if __name__ == "__main__":
    main()
