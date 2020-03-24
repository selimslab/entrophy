def sanitize_dict(d):
    return {k: v for k, v in d.items() if isinstance(k, str) and v is not None}
