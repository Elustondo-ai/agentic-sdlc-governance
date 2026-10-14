"""Read the flat string-only ASDLC agent TOML format on Python 3.9+.

Use the native TOML parser when available. The dependency-free older-Python
reader deliberately rejects tables, arrays and other unsupported value types.
"""
import json
import re

try:
    import tomllib
except ImportError:
    tomllib = None


def flat_strings(text):
    result = {}
    entry = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*("""[\s\S]*?"""|"(?:[^"\\\r\n]|\\.)*")[ \t]*(?:#[^\n]*)?(?:\n|$)')
    position = 0
    while position < len(text):
        skip = re.match(r'(?:\s+|#[^\n]*(?:\n|$))*', text[position:])
        position += skip.end()
        if position == len(text):
            break
        match = entry.match(text, position)
        if match is None:
            raise ValueError('Python 3.9 agent validation supports flat quoted-string TOML fields only')
        key, value = match.groups()
        if key in result:
            raise ValueError('Duplicate agent configuration key: ' + key)
        if value.startswith('"""'):
            value = value[3:-3]
            if value.startswith('\n'):
                value = value[1:]
            # JSON and this supported TOML subset share basic-string escapes.
            value = '"' + value.replace('\n', '\\n').replace('\t', '\\t').replace('\r', '\\r').replace('"', '\\"') + '"'
        result[key] = json.loads(value)
        position = match.end()
    return result


def loads(text):
    return tomllib.loads(text) if tomllib else flat_strings(text)
