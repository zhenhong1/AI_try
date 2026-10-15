语义层：用业务语言定义数据和指标的含义，例如“销售额怎么算”“有效订单是什么”。

YAML：一种便于人阅读和编辑的配置文件格式。

所以，语义层 YAML 就是用 YAML 文件，把数据库字段、业务概念和指标计算规则整理成明确、可复用的定义，供模型或查询系统参考


二、逐行理解 YAML
以这个例子为准：

metrics:                                                            
  sales_amount:                                                     
    description: 有效订单的销售额，扣除退款                                                                                     
    formula: amount - refund_amount                                                                                 
    filters:                                                                                                                                
      - status != "cancelled"                                                                                                       
    date_column: order_date                                                                                                         