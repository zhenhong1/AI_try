from pathlib import Path
import duckdb

SAMPLE = Path("data/sample")
DB = "data/shop.duckdb"

con = duckdb.connect(DB)
for f in sorted(SAMPLE.glob("*.csv")):
    name = f.stem                      # orders.csv -> orders
    con.execute(
        f"CREATE OR REPLACE TABLE {name} AS "
        f"SELECT * FROM read_csv_auto('{f.as_posix()}')"
    )
    n = con.execute(f"SELECT count(*) FROM {name}").fetchone()[0]
    print(f"{name:12s} {n:>6d} 行")
con.close()
