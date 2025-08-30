"""
Temporary compatibility shim for the removed stdlib `cgi` module in Python 3.13+.

This file provides a minimal API so Django (and other libraries) can import
`cgi` without failing. It is a stop-gap measure: it DOES NOT implement full
functionality of the original module. Use Python <=3.12 or upgrade libraries
for a proper fix.

If your app depends on advanced cgi features (FieldStorage, parse_multipart,
etc.), replace this shim with a proper implementation or run the project
under a supported Python version.
"""

class FieldStorage:
    def __init__(self, *args, **kwargs):
        # Minimal stub: creating this object will raise when used. The
        # presence of the class prevents import errors during Django setup
        # (most management commands don't actually parse request bodies).
        raise RuntimeError("cgi.FieldStorage is not available in this shim; use Python <=3.12 or provide a full replacement")


def parse_multipart(fp, pdict):
    # Not implemented. Raise to make the failure explicit if code tries to use it.
    raise NotImplementedError("cgi.parse_multipart is not implemented in the compatibility shim")


def escape(s, quote=True):
    # Minimal HTML-escape fallback for simple usage
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            .replace('"', '&quot;') if isinstance(s, str) else s)


def parse_header(line):
    """
    Parse a Content-type like header.
    
    Return the main value and a dictionary of options.
    
    This is a minimal implementation for compatibility with Django.
    """
    if not line:
        return '', {}
    
    parts = line.split(';')
    main_value = parts[0].strip()
    params = {}
    
    for part in parts[1:]:
        if '=' in part:
            key, value = part.split('=', 1)
            params[key.strip().lower()] = value.strip().strip('"')
    
    return main_value, params
