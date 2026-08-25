with open('app.py', 'r') as f:
    src = f.read()

old = """/* Disable browser copy popup / text selection highlight */
::selection { background: transparent; }
::-moz-selection { background: transparent; }"""

if old in src:
    src = src.replace(old, "", 1)
    with open('app.py', 'w') as f:
        f.write(src)
    print("done - text selection restored")
else:
    print("not found")

import ast
ast.parse(open('app.py').read())
print("syntax OK")
