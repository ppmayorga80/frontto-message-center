def deep_get(obj, *keys, default=None):
    current_obj = obj
    for key in keys:
        try:
            current_obj = current_obj[key]
        except Exception:
            return default
    return current_obj


if __name__ == '__main__':
    x = ["Hola", {"name": {"first": "Pedro", "last": "mayorga", "grades": [10, 20, 30]}}]

    print(deep_get(x, 0))
    print(deep_get(x, 10, default="EMPTY SET"))

    print(deep_get(x, 1, "name", "first"))
    print(deep_get(x, 1, "name", "last"))

    print(deep_get(x, 1, "name", "grades", 2))
    print(deep_get(x, 1, "name", "grades", 20, default="EMPTY SET"))
