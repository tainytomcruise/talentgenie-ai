from app_modular import app
from flask import url_for

def list_routes():
    import urllib
    output = []
    with app.app_context():
        for rule in app.url_map.iter_rules():
            methods = ','.join(sorted(rule.methods))
            url = urllib.parse.unquote(str(rule))
            output.append(f"{url} [{methods}]")
            
    for line in sorted(output):
        print(line)

if __name__ == "__main__":
    list_routes()
