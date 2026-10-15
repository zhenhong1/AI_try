"""生成模拟电商数据 -> data/sample/*.csv
固定种子，重复运行结果完全一致。
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42
random.seed(SEED)

OUT = Path("data/sample")
OUT.mkdir(parents=True, exist_ok=True)

N_CUSTOMERS = 1500
N_PRODUCTS = 200
N_ORDERS = 8000
START = date(2024, 1, 1)
END = date(2025, 6, 30)

REGIONS = {
    "East": ["Shanghai", "Hangzhou", "Nanjing"],
    "South": ["Guangzhou", "Shenzhen"],
    "North": ["Beijing", "Tianjin"],
    "West": ["Chengdu", "Xian"],
}
REGION_WEIGHTS = {"East": 0.40, "South": 0.25, "North": 0.20, "West": 0.15}

# 品类 -> (最低价, 最高价)
CATEGORIES = {
    "electronics": (100, 2000),
    "home": (20, 300),
    "beauty": (10, 200),
    "sports": (30, 500),
    "books": (5, 60),
    "toys": (10, 150),
}


def write_csv(name, header, rows):
    path = OUT / f"{name}.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"{name:12s} {len(rows):>6d} 行")


# ---------- customers ----------
customers = []
region_names = list(REGION_WEIGHTS)
region_probs = list(REGION_WEIGHTS.values())
for i in range(1, N_CUSTOMERS + 1):
    region = random.choices(region_names, region_probs)[0]
    city = random.choice(REGIONS[region])
    signup = START - timedelta(days=random.randint(0, 365))
    level = random.choices(["bronze", "silver", "gold"], [0.7, 0.2, 0.1])[0]
    customers.append([f"C{i:04d}", city, region, signup.isoformat(), level])
cust_region = {c[0]: c[2] for c in customers}

# ---------- products ----------
products = []
cat_names = list(CATEGORIES)
for i in range(1, N_PRODUCTS + 1):
    cat = random.choice(cat_names)
    lo, hi = CATEGORIES[cat]
    price = round(random.uniform(lo, hi), 2)
    cost = round(price * random.uniform(0.5, 0.8), 2)
    products.append([f"P{i:03d}", f"{cat}_item_{i}", cat, price, cost])
prod_price = {p[0]: p[3] for p in products}

# ---------- 下单日期：随时间增长，11 月有高峰 ----------
days = [START + timedelta(days=d) for d in range((END - START).days + 1)]
weights = []
for idx, d in enumerate(days):
    w = 1 + 1.5 * idx / len(days)          # 逐步增长
    if d.month == 11:
        w *= 2.0                            # 11 月高峰
    weights.append(w)

# ---------- orders / items / payments / reviews ----------
orders, items, payments, reviews = [], [], [], []
LAST_OPEN = END - timedelta(days=7)         # 最后 7 天的订单可能还在途

for i in range(1, N_ORDERS + 1):
    oid = f"O{i:05d}"
    cid = random.choice(customers)[0]
    region = cust_region[cid]
    odate = random.choices(days, weights)[0]

    if odate > LAST_OPEN:
        status = random.choices(["shipped", "delivered", "canceled"], [0.6, 0.3, 0.1])[0]
    else:
        status = random.choices(["delivered", "canceled", "returned"], [0.88, 0.07, 0.05])[0]

    # 配送天数
    delivered = None
    ddays = None
    if status in ("delivered", "returned"):
        ddays = random.randint(2, 7)
        if region == "West":
            ddays += 1
        if region == "West" and odate.year == 2024 and odate.month == 11:
            ddays += 5                      # 预埋异常：West 2024-11 变慢
        delivered = (odate + timedelta(days=ddays)).isoformat()

    orders.append([oid, cid, status, odate.isoformat(), delivered or ""])

    # 行项目
    n_items = random.choices([1, 2, 3, 4], [0.55, 0.28, 0.12, 0.05])[0]
    total = 0.0
    for k, pid in enumerate(random.sample(list(prod_price), n_items), start=1):
        qty = random.choices([1, 2, 3], [0.75, 0.2, 0.05])[0]
        unit = round(prod_price[pid] * random.uniform(0.9, 1.0), 2)
        items.append([oid, k, pid, qty, unit])
        total += qty * unit

    # 支付：已取消的订单没有支付记录
    if status != "canceled":
        method = random.choices(["alipay", "wechat", "card", "cod"],
                                [0.45, 0.35, 0.15, 0.05])[0]
        payments.append([oid, method, round(total, 2)])

    # 评价：已送达订单约 60% 有评价；配送慢则评分低
    if status == "delivered" and random.random() < 0.6:
        if ddays and ddays > 8:
            score = random.choices([1, 2, 3, 4, 5], [0.35, 0.30, 0.15, 0.12, 0.08])[0]
        else:
            score = random.choices([1, 2, 3, 4, 5], [0.04, 0.05, 0.10, 0.26, 0.55])[0]
        reviews.append([oid, score])

write_csv("customers", ["customer_id", "city", "region", "signup_date", "member_level"], customers)
write_csv("products", ["product_id", "product_name", "category", "price", "cost"], products)
write_csv("orders", ["order_id", "customer_id", "order_status", "order_date", "delivered_date"], orders)
write_csv("order_items", ["order_id", "item_no", "product_id", "quantity", "unit_price"], items)
write_csv("payments", ["order_id", "method", "amount"], payments)
write_csv("reviews", ["order_id", "review_score"], reviews)
