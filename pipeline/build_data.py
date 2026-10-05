"""Genera data/countries.json y data/proximity.json desde BACI (CEPII).

Uso:
  python pipeline/build_data.py --baci BACI_HS17_Y2022_V202401.csv \
      --countries country_codes_V202401.csv --products product_codes_HS17_V202401.csv --year 2022
Requiere: pip install pandas numpy
"""
import argparse, json, numpy as np, pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--baci", required=True); ap.add_argument("--countries", required=True)
ap.add_argument("--products"); ap.add_argument("--year", type=int, required=True)
ap.add_argument("--out", default="data"); ap.add_argument("--phi", type=float, default=0.55)
a = ap.parse_args()

df = pd.read_csv(a.baci, usecols=["t", "i", "j", "k", "v"])      # v en miles de US$
df = df[df.t == a.year]
df["hs4"] = df.k.astype(str).str.zfill(6).str[:4]
cc = pd.read_csv(a.countries).set_index("country_code")
names = cc.country_name.to_dict()
pn = {}
if a.products:
    p = pd.read_csv(a.products, dtype=str)
    pn = {c[:4]: d for c, d in zip(p.iloc[:, 0].str.zfill(6), p.iloc[:, 1])}

# Matriz país x producto y RCA de Balassa
X = df.groupby(["i", "hs4"]).v.sum().unstack(fill_value=0)
RCA = X.div(X.sum(1), axis=0).div(X.sum(0) / X.values.sum())
M = (RCA >= 1).astype(int)

# Proximidad: phi_ij = co-exportación / max(ubicuidad_i, ubicuidad_j)
ubi = M.sum(0).values
co = M.T.values @ M.values
phi = co / np.maximum.outer(ubi, ubi)
np.fill_diagonal(phi, 0)
prods = list(M.columns)
iu = np.argwhere(np.triu(phi >= a.phi))
edges = [{"s": prods[i], "t": prods[j], "phi": round(float(phi[i, j]), 3)} for i, j in iu]

# Salida por país
partners = df.groupby(["i", "j"]).v.sum()
out = {}
for c in X.index:
    tot = X.loc[c].sum()
    top = X.loc[c].nlargest(10)
    pt = partners.loc[c].nlargest(5)
    out[str(c)] = {
        "name": names.get(c, str(c)), "exports_usd_bn": round(tot / 1e6, 2),
        "top_products": [{"name": f"{pn.get(k, k)} ({k})", "share": round(v / tot, 4), "rca": round(RCA.loc[c, k], 2)} for k, v in top.items()],
        "partners": [{"name": names.get(j, str(j)), "share": round(v / tot, 4)} for j, v in pt.items()],
        "rca_products": [k for k in prods if M.loc[c, k]],
    }
meta = {"year": a.year, "source": "BACI (CEPII)", "illustrative": False}
json.dump({"meta": meta, "countries": out}, open(f"{a.out}/countries.json", "w"), ensure_ascii=False)
json.dump({"phi_min": a.phi, "edges": edges}, open(f"{a.out}/proximity.json", "w"))
print(f"{len(out)} países, {len(prods)} productos, {len(edges)} vínculos")
