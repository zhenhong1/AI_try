import sys
import duckdb
sys.path.insert(0, ".")
from evals.golden_seed import GOLDEN

con = duckdb.connect("data/shop.duckdb", read_only=True)

for g in GOLDEN:
    print(f"\n===== {g['id']} {g['question']}")
    print("口径：", g["caliber"])
    print(con.execute(g["sql"]).df().to_string(index=False))
