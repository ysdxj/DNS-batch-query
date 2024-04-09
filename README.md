# DNS批量查询
批量查询域名的DNS解析记录，支持指定DNS服务器，指定解析类型
```
usage: DNS-batch-query.py [-h] -d DOMAINS [-t TYPES]

批量查询DNS记录并保存到CSV文件。

options:
  -h, --help            show this help message and exit
  -d DOMAINS, --domains DOMAINS
                        包含域名列表的文件路径。
  -t TYPES, --types TYPES
                        查询的DNS记录类型，使用逗号分隔。如果未指定，则查询A, AAAA, CNAME类型。
```
eg
```
python DNS-batch-query.py -d domains.txt
python DNS-batch-query.py -d domains.txt -t A
```
![image](https://github.com/ysdxj/DNS-batch-query/assets/86157883/465b7bfe-567f-4dc6-84e7-314e02253625)
![image](https://github.com/ysdxj/DNS-batch-query/assets/86157883/7c371d10-72ff-4d5c-b83c-475823193fbc)
