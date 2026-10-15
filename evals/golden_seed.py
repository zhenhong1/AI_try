GOLDEN = [
    {
        "id": "Q1", "question": "订单总数是多少？",
        "caliber": "所有状态的订单都计入。",
        "sql": "SELECT count(*) AS order_cnt FROM orders",
    },
    {
        "id": "Q2", "question": "各订单状态各有多少单？",
        "caliber": "无歧义。",
        "sql": """SELECT order_status, count(*) AS cnt
                  FROM orders GROUP BY order_status ORDER BY cnt DESC""",
    },
    {
        "id": "Q3", "question": "销售额最高的前 5 个品类是什么？",
        "caliber": "销售额 = SUM(quantity*unit_price)；排除 canceled 和 returned，保留 delivered 与 shipped。",
        "sql": """SELECT p.category, round(sum(oi.quantity * oi.unit_price), 2) AS sales
                  FROM order_items oi
                  JOIN orders o   ON o.order_id = oi.order_id
                  JOIN products p ON p.product_id = oi.product_id
                  WHERE o.order_status NOT IN ('canceled', 'returned')
                  GROUP BY p.category ORDER BY sales DESC LIMIT 5""",
    },
    {
        "id": "Q4", "question": "每月订单量趋势如何？",
        "caliber": "按下单日期（order_date）分月；所有状态都计入，因为'订单量'指下单行为。",
        "sql": """SELECT date_trunc('month', order_date) AS month, count(*) AS order_cnt
                  FROM orders GROUP BY 1 ORDER BY 1""",
    },
    {
        "id": "Q5", "question": "平均配送天数是多少？",
        "caliber": "只统计 delivered 订单；配送天数 = delivered_date - order_date；NULL 不参与。",
        "sql": """SELECT round(avg(date_diff('day', order_date, delivered_date)), 2) AS avg_days
                  FROM orders
                  WHERE order_status = 'delivered' AND delivered_date IS NOT NULL""",
    },
    {
        "id": "Q6", "question": "评分低于 3 分的评价占比是多少？",
        "caliber": "分母是所有评价（reviews 表的行数），不是所有订单；低于 3 即 1、2 分。",
        "sql": """SELECT round(count(*) FILTER (WHERE review_score < 3) * 1.0 / count(*), 4) AS low_ratio
                  FROM reviews""",
    },
]
