ITEMS = [{'id': 1, 'title': 'Buy milk', 'description': 'Remember blue carton'}]


def search(query):
    fields = ['title']  # Deliberate bug: description omitted
    return [item for item in ITEMS if any(query.lower() in item[key].lower() for key in fields)]
