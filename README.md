# Atlas de comercio

Mapa interactivo de datos de comercio. Hosting gratuito en GitHub Pages; Python solo corre en tu computador para generar los datos.

## Estructura
- `index.html`: la página (D3, sin build ni dependencias que instalar).
- `data/countries.json`: datos por país (ahora son **datos de ejemplo**).
- `pipeline/build_data.py`: calcula exportaciones, RCA y proximidad desde BACI.

## Probar en local
    python -m http.server   # y abrir http://localhost:8000

## Publicar
1. Sube la carpeta a un repo de GitHub.
2. Settings > Pages > Deploy from a branch > `main` / root.
3. La página queda en `https://TU-USUARIO.github.io/NOMBRE-REPO/`.

## Datos reales
1. Descarga BACI desde cepii.fr (un año, HS6) junto con `country_codes` y `product_codes`.
2. `pip install pandas numpy`
3. `python pipeline/build_data.py --baci ... --countries ... --products ... --year 2022`
4. Commit de `data/*.json`.

Si algún país no se pinta, agrega su nombre en `ALIASES` dentro de `index.html`.

## Próximos pasos
- Selector de año y de producto.
- Calculadora de RCA en el navegador (`rca_products` ya sale en el JSON).
- Product space: `data/proximity.json` + Cytoscape.js, coloreando nodos con RCA ≥ 1.
- Reconstruir los datos automáticamente con GitHub Actions al subir un CSV nuevo.
