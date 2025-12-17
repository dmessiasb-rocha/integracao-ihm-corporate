import json
import os
import zipfile
from xml.sax.saxutils import escape


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def _p(text: str, style: str | None = None) -> str:
    # Basic Word paragraph with optional style.
    t = escape(text)
    if style:
        return (
            f"<w:p><w:pPr><w:pStyle w:val=\"{escape(style)}\"/></w:pPr>"
            f"<w:r><w:t xml:space=\"preserve\">{t}</w:t></w:r></w:p>"
        )
    return f"<w:p><w:r><w:t xml:space=\"preserve\">{t}</w:t></w:r></w:p>"


def _code_block(text: str) -> str:
    # Render code as normal paragraphs (Word without custom styles); keep indentation.
    # Split to avoid very long single <w:t> runs.
    parts = []
    for line in text.splitlines() or [""]:
        parts.append(_p(line))
    return "".join(parts)


def _resolve_ref(spec: dict, schema: dict) -> dict:
    ref = schema.get("$ref")
    if not ref:
        return schema
    if not ref.startswith("#/components/schemas/"):
        return schema
    name = ref.split("/")[-1]
    return spec.get("components", {}).get("schemas", {}).get(name, schema)


def _example_for_schema(spec: dict, schema: dict, depth: int = 0, seen: set | None = None):
    if seen is None:
        seen = set()

    if depth > 4:
        return None

    if "$ref" in schema:
        ref = schema["$ref"]
        if ref in seen:
            return None
        seen.add(ref)
        return _example_for_schema(spec, _resolve_ref(spec, schema), depth + 1, seen)

    t = schema.get("type")
    fmt = schema.get("format")

    if t == "object" or (t is None and "properties" in schema):
        props = schema.get("properties", {})
        required = schema.get("required", [])
        obj = {}

        # Include all required props, plus up to 3 optional props.
        optional_keys = [k for k in props.keys() if k not in required]
        keys = list(required) + optional_keys[:3]

        for k in keys:
            obj[k] = _example_for_schema(spec, props[k], depth + 1, seen.copy())
        return obj

    if t == "array":
        item_schema = schema.get("items", {})
        return [ _example_for_schema(spec, item_schema, depth + 1, seen.copy()) ]

    if t == "integer":
        return 0
    if t == "number":
        return 0.0
    if t == "boolean":
        return True

    # strings
    if fmt == "date-time":
        return "2025-01-01T00:00:00Z"
    if fmt == "byte":
        return "BASE64=="
    return "string"


def _collect_operations(spec: dict):
    paths = spec.get("paths", {})
    for path, path_item in sorted(paths.items()):
        if not isinstance(path_item, dict):
            continue
        for method in ["get", "post", "put", "delete", "patch"]:
            if method in path_item:
                op = path_item[method]
                yield path, method.upper(), op


def build_docx(spec: dict, output_path: str):
    title = spec.get("info", {}).get("title", "OpenAPI")
    version = spec.get("info", {}).get("version", "")
    desc = spec.get("info", {}).get("description", "")

    body = []
    body.append(_p(title, "Heading1"))
    if version:
        body.append(_p(f"Versão: {version}"))
    if desc:
        body.append(_p(desc))

    # Auth
    sec = spec.get("security")
    if sec:
        body.append(_p("Autenticação", "Heading2"))
        body.append(_p("Esta API requer autenticação via Bearer Token (JWT)."))

    body.append(_p("Endpoints", "Heading2"))

    for path, method, op in _collect_operations(spec):
        summary = op.get("summary", "")
        op_desc = op.get("description", "")

        body.append(_p(f"{method} {path}", "Heading3"))
        if summary:
            body.append(_p(f"Resumo: {summary}"))
        if op_desc:
            body.append(_p(op_desc))

        # Parameters
        params = op.get("parameters", [])
        if params:
            body.append(_p("Parâmetros", "Heading4"))
            for prm in params:
                name = prm.get("name", "")
                loc = prm.get("in", "")
                req = prm.get("required", False)
                sch = prm.get("schema", {})
                typ = sch.get("type", "")
                body.append(_p(f"- {name} ({loc}) {'obrigatório' if req else 'opcional'}: {typ}"))

        # Request example
        rb = op.get("requestBody")
        if rb:
            content = rb.get("content", {}).get("application/json", {})
            schema = content.get("schema")
            if schema:
                ex = _example_for_schema(spec, schema)
                body.append(_p("Exemplo de Request (application/json)", "Heading4"))
                body.append(_code_block(json.dumps(ex, ensure_ascii=False, indent=2)))

        # Response example (pick 200/201)
        responses = op.get("responses", {})
        resp_code = "200" if "200" in responses else ("201" if "201" in responses else None)
        if resp_code:
            resp = responses.get(resp_code, {})
            content = resp.get("content", {}).get("application/json", {})
            schema = content.get("schema")
            if schema:
                ex = _example_for_schema(spec, schema)
                body.append(_p(f"Exemplo de Response ({resp_code})", "Heading4"))
                body.append(_code_block(json.dumps(ex, ensure_ascii=False, indent=2)))

    document_xml = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        f"<w:document xmlns:w=\"{W_NS}\" xmlns:r=\"{R_NS}\">"
        "<w:body>"
        + "".join(body)
        + "<w:sectPr><w:pgSz w:w=\"11906\" w:h=\"16838\"/></w:sectPr>"
        "</w:body></w:document>"
    )

    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
"""

    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""

    # No external relationships needed
    doc_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>
"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", document_xml)
        z.writestr("word/_rels/document.xml.rels", doc_rels)


def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        spec = json.load(f)

    build_docx(spec, args.output)


if __name__ == "__main__":
    main()
