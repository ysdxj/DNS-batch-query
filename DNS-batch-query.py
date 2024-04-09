import argparse
import os
import pandas as pd
import dns.resolver

# 解析命令行参数
def parse_arguments():
    parser = argparse.ArgumentParser(description='批量查询DNS记录并保存到CSV文件，并在控制台同步显示查询结果和进度。')
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
def query_dns_records(domain, resolvers, record_types, current_index, total_domains):
    results = []  # 存储所有成功的查询结果
    for record_type in record_types:
        found = False
        for resolver in resolvers:
            try:
                answers = resolver.resolve(domain, record_type)
                results.append({
                    'dns_server': resolver.nameservers[0],
                    'record_type': record_type,
                    'answers': ", ".join([answer.to_text() for answer in answers])
                })
                print(f"查询成功: {domain} {record_type} 记录，使用DNS服务器 {resolver.nameservers[0]}")
                found = True
                break  # 成功后即停止尝试其他DNS服务器
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout, dns.exception.DNSException):
                continue
        if not found:
            print(f"查询失败: {domain} 未找到 {record_type} 记录")
    progress = (current_index + 1) / total_domains * 100
    print(f"进度: {current_index + 1}/{total_domains} ({progress:.2f}%)")
    return results

# 保存结果到CSV文件，处理文件已存在的情况
def save_to_csv(df, filename='dns_records.csv'):
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

def main():
    args = parse_arguments()
    domains = read_domains_from_file(args.domains)
    record_types = args.types.split(',')
    dns_servers = read_dns_servers_from_file()
    resolvers = [set_custom_dns_server(server) for server in dns_servers]

    results = []
    for index, domain in enumerate(domains):
        query_results = query_dns_records(domain, resolvers, record_types, index, len(domains))
        for result in query_results:
            results.append({
                '域名': domain,
                'DNS服务器': result.get('dns_server', '未知DNS服务器'),
                '记录类型': result.get('record_type', '无记录类型'),
                '记录值': result.get('answers', "无记录")
            })

    df = pd.DataFrame(results)
    save_to_csv(df)

if __name__ == "__main__":
    main()
