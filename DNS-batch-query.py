import argparse
import os
import pandas as pd
import dns.resolver

# 解析命令行参数
def parse_arguments():
    parser = argparse.ArgumentParser(description='批量查询DNS记录并保存到CSV文件。')
    parser.add_argument('-d', '--domains', required=True, help='包含域名列表的文件路径。')
    parser.add_argument('-t', '--types', default='A,AAAA,CNAME', help='查询的DNS记录类型，使用逗号分隔。如果未指定，则查询A, AAAA, CNAME类型。')
    return parser.parse_args()

# 读取域名列表
def read_domains_from_file(filename):
    with open(filename, 'r') as file:
        return file.read().splitlines()

# 读取DNS服务器列表
def read_dns_servers_from_file(filename='dns_servers.txt'):
    with open(filename, 'r') as file:
        return file.read().splitlines()

# 设置自定义DNS服务器
def set_custom_dns_server(server):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [server]
    return resolver

# 查询DNS记录并打印查询过程及进度
def query_dns_records(domain, resolvers, record_types):
    results = []  # 用于存储查询结果
    for record_type in record_types:
        for resolver in resolvers:
            try:
                answers = resolver.resolve(domain, record_type)
                record = {
                    '域名': domain,
                    'DNS服务器': resolver.nameservers[0],
                    '记录类型': record_type,
                    '记录值': ", ".join([answer.to_text() for answer in answers])
                }
                results.append(record)
                print(f"查询成功: {domain} {record_type} 记录，记录值: {record['记录值']}，使用DNS服务器 {resolver.nameservers[0]}")
                break
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout, dns.exception.DNSException):
                print(f"查询失败: {domain} 未找到 {record_type} 记录")
                break  # 如果查询失败，则跳过当前记录类型
    return results

def main():
    args = parse_arguments()
    domains = read_domains_from_file(args.domains)
    record_types = args.types.split(',')
    dns_servers = read_dns_servers_from_file()
    resolvers = [set_custom_dns_server(server) for server in dns_servers]

    all_results = []  # 存储所有查询结果
    for index, domain in enumerate(domains):
        query_results = query_dns_records(domain, resolvers, record_types)
        all_results.extend(query_results)
        print(f"进度: {index + 1}/{len(domains)}")

    df = pd.DataFrame(all_results)
    
    # 处理文件已存在的情况
    filename = 'dns_records.csv'
    if os.path.exists(filename):
        print(f"{filename} 文件已存在。")
        choice = input("选择操作：[1] 覆盖 [2] 追加 [3] 取消 : ")
        if choice == '1':
            df.to_csv(filename, mode='w', index=False, encoding='utf_8_sig')
            print(f"数据已覆盖保存到 {filename}")
        elif choice == '2':
            df.to_csv(filename, mode='a', header=False, index=False, encoding='utf_8_sig')
            print(f"数据已追加到 {filename}")
        else:
            print("操作已取消。")
    else:
        df.to_csv(filename, index=False, encoding='utf_8_sig')
        print(f"数据已保存到 {filename}")

if __name__ == "__main__":
    main()