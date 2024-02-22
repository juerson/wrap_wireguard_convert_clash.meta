import yaml
import logging
import os
import ipaddress

FILES = ["wg_config.yaml", "rules.txt"]
BASE_CONFIG = r"""mode: rule
port: 7890
socks-port: 7891
allow-lan: false
log-level: info
secret: ''
unified-delay: true
external-controller: :9097
global-client-fingerprint: chrome
dns:
  enable: true
  listen: :53
  ipv6: false
  enhanced-mode: fake-ip
  fake-ip-range: 198.18.0.1/16
  default-nameserver:
    - 223.5.5.5
    - 8.8.8.8
    - 1.1.1.1
  nameserver:
    - https://dns.alidns.com/dns-query
    - https://doh.pub/dns-query
  fallback:
    - https://1.0.0.1/dns-query
    - tls://dns.google
  fallback-filter:
    geoip: true
    geoip-code: CN
    ipcidr:
      - 240.0.0.0/4
"""
PROXY_GROUPS = {
    "select_group": """  - name: 🔰 节点选择
    type: select
    proxies:
      - ♻️ 自动选择
      - 🎯 全球直连
""",
    "auto_group": """  - name: ♻️ 自动选择
    type: url-test
    url: http://www.gstatic.com/generate_204
    interval: 300
    proxies:
""",
    "netflix_group": """  - name: 🎥 NETFLIX
    type: select
    proxies:
      - 🔰 节点选择
      - ♻️ 自动选择
      - 🎯 全球直连
""",
    "homeless_exile_group": """  - name: 🐟 漏网之鱼
    type: select
    proxies:
      - 🔰 节点选择
      - 🎯 全球直连
      - ♻️ 自动选择
""",
    "telegram_group": """  - name: 📲 电报信息
    type: select
    proxies:
      - 🔰 节点选择
      - 🎯 全球直连
""",
    "microsoft_group": """  - name: Ⓜ️ 微软服务
    type: select
    proxies:
      - 🎯 全球直连
      - 🔰 节点选择
""",
    "apple_group": """  - name: 🍎 苹果服务
    type: select
    proxies:
      - 🔰 节点选择
      - 🎯 全球直连
      - ♻️ 自动选择
""",
    "foreign_media_group": """  - name: 🌍 国外媒体
    type: select
    proxies:
      - 🔰 节点选择
      - ♻️ 自动选择
      - 🎯 全球直连
""",
    "national_media_group": """  - name: 🌏 国内媒体
    type: select
    proxies:
      - 🎯 全球直连
      - 🔰 节点选择
""",
    "hijacking_group": """  - name: 🚫 运营劫持
    type: select
    proxies:
      - 🛑 全球拦截
      - 🎯 全球直连
      - 🔰 节点选择
""",
    "adblock_group": """  - name: ⛔️ 广告拦截
    type: select
    proxies:
      - 🛑 全球拦截
      - 🎯 全球直连
      - 🔰 节点选择
""",
    "global_block_group": """  - name: 🛑 全球拦截
    type: select
    proxies:
      - REJECT
      - DIRECT
""",
    "direct_group": """  - name: 🎯 全球直连
    type: select
    proxies:
      - DIRECT
"""
}


class FileHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def read_yaml_info(self, file_path):
        # 验证文件路径
        if not os.path.exists(file_path):
            self.logger.error(f"文件不存在： {file_path}")
            return None

        with open(file_path, mode='r', encoding='utf-8') as stream:
            try:
                data = yaml.safe_load(stream)
                if not data:  # 如果文件内容为空
                    self.logger.error(f"YAML文件为空！")
                return data
            except yaml.YAMLError as exc:
                self.logger.error(f"YAML解析错误： {exc}")
                return None
            except Exception as e:
                self.logger.error(f"读取YAML文件时发生错误： {e}")
                return None

    def read_txt_server(self, file_path):
        # 验证文件路径
        if not os.path.exists(file_path):
            self.logger.error(f"文件不存在： {file_path}")
            return None

        with open(file_path, mode='r', encoding='utf-8') as f:
            try:
                servers = f.readlines()
                servers_strip = {server.strip() for server in servers if server != ""}
                if len(servers_strip) == 0:
                    self.logger.error(f"server.txt文件为空！")
                return list(servers_strip)
            except Exception as e:
                self.logger.error(f"读取server文件时发生错误： {e}")
                return None

    def read_txt_rules(self, file_path):
        # 验证文件路径
        if not os.path.exists(file_path):
            self.logger.error(f"文件不存在： {file_path}")
            return None

        with open(file_path, mode="r", encoding="utf-8") as f:
            try:
                data = f.read()
                if not data:
                    self.logger.error(f"rules.txt文件为空！")
                return data
            except Exception as e:
                self.logger.error(f"读取rules文件时发生错误： {e}")
                return None


def generate_ips_from_cidr(cidr):
    network = ipaddress.ip_network(cidr)
    return network.hosts()


if __name__ == '__main__':
    port = 2408  # 写入配置的，全部都用这个端口
    # 设置日志记录器的配置
    logging.basicConfig(level=logging.ERROR)
    handler = FileHandler()
    conf = handler.read_yaml_info(FILES[0])
    RULES = handler.read_txt_rules(FILES[1])
    cidrs = [
        "188.114.96.0/24",
        "188.114.97.0/24",
        "188.114.98.0/24",
        "188.114.99.0/24",
        "162.159.192.0/24",
        "162.159.193.0/24",
        "162.159.195.0/24",
    ]
    ips = []
    for cidr in cidrs:
        ips.extend([str(ip) for ip in generate_ips_from_cidr(cidr)])
    if conf and RULES:  # 读取到的内容合法，才执行下面的步骤
        node_names = []
        node_li = ["proxies:\n", ]
        for server in ips:
            name = f"{server}:{port}"
            conf["name"] = name
            conf["server"] = server
            conf["port"] = port
            node_names.append(name)
            node_info_str = f"  - {str(conf).replace(": True", ": true").replace(": False", ": false")}\n"
            node_li.append(node_info_str)
        node_names = [f"      - {item}" for item in node_names]
        proxy_groups_string = ""
        proxies = "".join(node_li)
        for k, v in PROXY_GROUPS.items():
            if k in ["select_group", "auto_group", "netflix_group", "homeless_exile_group", "telegram_group",
                     "microsoft_group", "apple_group", "foreign_media_group"]:
                proxy_groups_string += (v + "\n".join(node_names) + "\n")  # 这个添加节点名称
            else:
                proxy_groups_string += v  # 这个不需要添加节点名称
        # 构建clash的全部信息
        clash_content = BASE_CONFIG + proxies + "proxy-groups:\n" + proxy_groups_string + RULES
        with open("clash.yaml", mode="w", encoding="utf-8") as wf:
            wf.write(clash_content)
