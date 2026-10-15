# 指标口径（v0）

| 指标 | 定义 | 过滤条件 | 备注 |
|---|---|---|---|
| 订单量 | count(orders) | 无，含所有状态 | 下单行为 |
| 销售额 | sum(quantity*unit_price) | status NOT IN (canceled, returned) | 含 shipped |
| 平均配送天数 | avg(delivered_date - order_date) | status = delivered | NULL 不参与 |
| 低分评价占比 | count(score<3)/count(reviews) | 无 | 分母是评价数 |
