class Photo:
    def __init__(self, json):
        self.json = json

    @property
    def url(self):
        src_keys = {key: key for key in self.json if key.startswith('src')}
        size2key = {int("".join(c for c in value if c.isdecimal())): key
                    for key, value in src_keys.items()}
        sorted_sizes = sorted(list(size2key.keys()), reverse=True)
        key = size2key[sorted_sizes[0]]
        url = self.json[key]
        return url