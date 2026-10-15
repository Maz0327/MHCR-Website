"""Tiny template renderer for the MHCR build (Python 3 stdlib only).

Syntax (everything else is copied as-is):
  {{path.to.value}}                 HTML-escaped value. A missing name is a build error, never a blank.
  {{& path}}                        raw value (only for HTML the build made itself, e.g. {{& content}})
  {{> name}}                        include partials/name.html, rendered in the same scope
  {{#each path}} .. {{/each}}       loop. Inside: names resolve on the item first, then outward.
                                    {{.}} = the item itself, {{@n}} = 1-based index, {{@first}} / {{@last}}
  {{#if path}} .. {{else}} .. {{/if}}   truthy test ({{#unless path}} .. {{/unless}} is the inverse)
  {{helper arg arg key="value" key=name}}  call a helper (build.py registers `pic` and `json`).
                                    An arg that resolves as a name gives its value; anything else is a literal.
                                    key="text" is literal; key=name (no quotes) must resolve.
"""
import html
import re

TAG = re.compile(r"\{\{(.*?)\}\}", re.S)
ARG = re.compile(r'([A-Za-z_][\w-]*)=(?:"([^"]*)"|([^\s"]+))|"([^"]*)"|(\S+)')


class TemplateError(Exception):
    pass


def parse(src, name):
    """Source -> nested node list. Nodes: ('text', s) ('var', path, raw) ('call', name, args, kwargs) ('block', kind, path, body, else)."""
    pos, stack = 0, [("root", None, [], None)]
    for m in TAG.finditer(src):
        if m.start() > pos:
            stack[-1][2].append(("text", src[pos:m.start()]))
        pos = m.end()
        t = m.group(1).strip()
        if t.startswith(("#each ", "#if ", "#unless ")):
            kind, path = t[1:].split(None, 1)
            stack.append((kind, path.strip(), [], None))
        elif t == "else":
            kind, path, body, _ = stack[-1]
            if kind not in ("if", "unless"):
                raise TemplateError(f"{name}: {{{{else}}}} outside #if")
            stack[-1] = (kind, path, [], body)          # body so far becomes the "then" part
        elif t.startswith("/"):
            kind, path, body, then = stack.pop()
            if kind != t[1:].strip():
                raise TemplateError(f"{name}: {{{{{t}}}}} closes #{kind}")
            node = ("block", kind, path, then if then is not None else body, body if then is not None else [])
            stack[-1][2].append(node)
        elif t.startswith(">"):
            stack[-1][2].append(("partial", t[1:].strip()))
        elif t.startswith("&"):
            stack[-1][2].append(("var", t[1:].strip(), True))
        elif " " in t:
            fn, rest = t.split(None, 1)
            args, kwargs = [], {}
            for k, kv, kname, q, bare in ARG.findall(rest):
                if k:
                    kwargs[k] = ("lit", kv) if not kname else ("name", kname)
                else:
                    args.append(("lit", q) if q or not bare else ("name", bare))
            stack[-1][2].append(("call", fn, args, kwargs))
        else:
            stack[-1][2].append(("var", t, False))
    if len(stack) != 1:
        raise TemplateError(f"{name}: unclosed #{stack[-1][0]} {stack[-1][1]}")
    stack[-1][2].append(("text", src[pos:]))
    return stack[0][2]


MISSING = object()


def lookup(scopes, path):
    if path == ".":
        return scopes[-1]
    first, *rest = path.split(".")
    for sc in reversed(scopes):
        if isinstance(sc, dict) and first in sc:
            val = sc[first]
            break
    else:
        return MISSING
    for part in rest:
        if isinstance(val, dict) and part in val:
            val = val[part]
        else:
            return MISSING
    return val


class Renderer:
    """partials: callable(name) -> source text. helpers: {name: fn(*args, scopes=..., **kwargs) -> html}."""

    def __init__(self, partials, helpers):
        self.partials, self.helpers, self.cache = partials, helpers, {}

    def render(self, src, scopes, name="template", depth=0):
        key = (name, src)
        if key not in self.cache:
            self.cache[key] = parse(src, name)
        return self._nodes(self.cache[key], list(scopes), name, depth)

    def _need(self, scopes, path, name):
        val = lookup(scopes, path)
        if val is MISSING:
            raise TemplateError(f"{name}: unknown name {{{{{path}}}}}")
        return val

    def _nodes(self, nodes, scopes, name, depth):
        out = []
        for n in nodes:
            kind = n[0]
            if kind == "text":
                out.append(n[1])
            elif kind == "var":
                val = self._need(scopes, n[1], name)
                out.append(str(val) if n[2] else html.escape(str(val), quote=True))
            elif kind == "partial":
                if depth > 12:
                    raise TemplateError(f"{name}: partials nested too deep (loop?) at {n[1]}")
                out.append(self.render(self.partials(n[1]), scopes, f"partials/{n[1]}.html", depth + 1))
            elif kind == "call":
                fn = self.helpers.get(n[1])
                if not fn:
                    raise TemplateError(f"{name}: unknown helper {n[1]!r}")
                args = []
                for typ, v in n[2]:
                    val = lookup(scopes, v) if typ == "name" else MISSING
                    args.append(v if val is MISSING else val)
                kwargs = {k: (v if typ == "lit" else self._need(scopes, v, name)) for k, (typ, v) in n[3].items()}
                try:
                    out.append(fn(*args, scopes=scopes, **kwargs))
                except (ValueError, KeyError, FileNotFoundError) as e:
                    raise TemplateError(f"{name}: {{{{{n[1]} ...}}}}: {e}") from e
            else:
                _, block, path, body, other = n
                val = self._need(scopes, path, name)
                if block == "each":
                    items = list(val or [])
                    for i, item in enumerate(items):
                        meta = {"@n": i + 1, "@first": i == 0, "@last": i == len(items) - 1}
                        out.append(self._nodes(body, scopes + [meta, item], name, depth))
                else:
                    truthy = bool(val) if block == "if" else not val
                    out.append(self._nodes(body if truthy else other, scopes, name, depth))
        return "".join(out)
