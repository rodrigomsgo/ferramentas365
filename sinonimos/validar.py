import json, re, unicodedata
from collections import Counter

def norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")

# prefixo: tolera flexão de gênero, número e conjugação
def prefixo(w):
    w = norm(w)
    return w[: max(4, len(w) - 2)]

def casa(base, tokens):
    p = prefixo(base)
    return any(norm(t).startswith(p) for t in tokens)

d = json.load(open("banco-sinonimos.json"))
P = d["palavras"]
erros = []

print(f"total de entradas: {len(P)}")
print("por classe:", dict(Counter(p["classe"] for p in P)))
print("sinônimos:", dict(sorted(Counter(len(p["sinonimos"]) for p in P).items())))
print(f"total de sinônimos: {sum(len(p['sinonimos']) for p in P)}\n")

vistas = set()
for p in P:
    w, sins, frase = p["palavra"], p["sinonimos"], p["frase"]

    if norm(w) in vistas:
        erros.append(f"[{w}] palavra duplicada no banco")
    vistas.add(norm(w))

    if not 3 <= len(sins) <= 6:
        erros.append(f"[{w}] tem {len(sins)} sinônimos (esperado 3–6)")

    if len(set(map(norm, sins))) != len(sins):
        erros.append(f"[{w}] sinônimos repetidos entre si")

    if norm(w) in map(norm, sins):
        erros.append(f"[{w}] a própria palavra está na lista de sinônimos")

    tokens = re.findall(r"[\wÀ-ÿ]+", frase)

    if not casa(w, tokens):
        erros.append(f"[{w}] a frase não usa a palavra principal: {frase!r}")

    for s in sins:
        if casa(s, tokens):
            erros.append(f"[{w}] VAZAMENTO: o sinônimo '{s}' aparece na frase {frase!r}")

    if not frase.endswith((".", "!", "?")):
        erros.append(f"[{w}] frase sem pontuação final")

if erros:
    print(f"{len(erros)} problema(s):")
    for e in erros:
        print(" -", e)
else:
    print("Nenhum problema encontrado.")
