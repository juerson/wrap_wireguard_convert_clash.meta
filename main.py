import random

import yaml
import logging
import os
import ipaddress

FILES = ["resources/wg_config.yaml", "resources/rules.txt"]
BASE_CONFIG = r"""mode: rule
port: 7890
socks-port: 7891
allow-lan: false
log-level: info
external-controller: :9090
global-client-fingerprint: chrome
dns:
  enable: true
  listen: :53
  default-nameserver: [223.5.5.5, 119.29.29.29]
  ipv6: false
  enhanced-mode: fake-ip
  fake-ip-filter: ["*.n.n.srv.nintendo.net", +.stun.playstation.net, xbox.*.*.microsoft.com, "*.msftncsi.com", "*.msftconnecttest.com", WORKGROUP, "*.lan", stun.*.*.*, stun.*.*, time.windows.com, time.nist.gov, time.apple.com, time.asia.apple.com, "*.ntp.org.cn", "*.openwrt.pool.ntp.org", time1.cloud.tencent.com, time.ustc.edu.cn, pool.ntp.org, ntp.ubuntu.com, "*.*.xboxlive.com", speedtest.cros.wr.pvp.net]
  nameserver: [tls://223.5.5.5:853, https://223.6.6.6/dns-query, https://120.53.53.53/dns-query]
  nameserver-policy: {+.tmall.com: 223.5.5.5, +.taobao.com: 223.5.5.5, +.alicdn.com: 223.5.5.5, +.aliyun.com: 223.5.5.5, +.alipay.com: 223.5.5.5, +.alibaba.com: 223.5.5.5, +.qq.com: 119.29.29.29, +.tencent.com: 119.29.29.29, +.weixin.com: 119.29.29.29, +.qpic.cn: 119.29.29.29, +.jd.com: 119.29.29.29, +.bilibili.com: 119.29.29.29, +.hdslb.com: 119.29.29.29, +.163.com: 119.29.29.29, +.126.com: 119.29.29.29, +.126.net: 119.29.29.29, +.127.net: 119.29.29.29, +.netease.com: 119.29.29.29, +.baidu.com: 223.5.5.5, +.bdstatic.com: 223.5.5.5, +.bilivideo.+: 119.29.29.29, +.iqiyi.com: 119.29.29.29, +.douyinvod.com: 180.184.1.1, +.douyin.com: 180.184.1.1, +.douyincdn.com: 180.184.1.1, +.douyinpic.com: 180.184.1.1, +.feishu.cn: 180.184.1.1}
  fallback: [tls://101.101.101.101:853,https://101.101.101.101/dns-query, https://public.dns.iij.jp/dns-query, https://208.67.220.220/dns-query]
  fallback-filter: {geoip: true, ipcidr: [240.0.0.0/4, 0.0.0.0/32, 127.0.0.1/32], domain: [+.google.com, +.facebook.com, +.twitter.com, +.youtube.com, +.xn--ngstr-lra8j.com, +.google.cn, +.googleapis.cn, +.googleapis.com, +.gvt1.com, +.paoluz.com, +.paoluz.link, +.paoluz.xyz, +.sodacity-funk.xyz, +.nloli.xyz,+.jsdelivr.net, +.proton.me]}
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
    # 随机的端口的列表
    ports = [854, 859, 864, 878, 880, 890, 891, 894, 903, 908, 928, 934, 939, 942, 943, 945, 946, 955, 968, 987, 988,
             1002, 1010, 1014, 1018, 1070, 1074, 1180, 1387, 1843, 2371, 2506, 3138, 3476, 3581, 3854, 4177, 4198, 4233,
             5279, 5956, 7103, 7152, 7156, 7281, 7559, 8319, 8742, 8854, 8886, 2408, 500, 4500, 1701]
    # 设置日志记录器的配置
    logging.basicConfig(level=logging.ERROR)
    handler = FileHandler()
    conf = handler.read_yaml_info(FILES[0])
    RULES = handler.read_txt_rules(FILES[1])
    default_port = conf.get("port")
    try:
        if int(default_port) in ports:
            port = default_port  # 如果配置文件中有端口且是cf udp的端口，就使用配置文件中的端口
        else:
            raise ValueError
    except ValueError:
        port = random.choice(ports)  # 如果配置文件中的端口不合法，就从ports列表中随机选择一个
    # 使用嵌套列表，便于拆分数据，使用不同的文件保存
    cidrs_li = [["188.114.96.0/24", "188.114.97.0/24", "188.114.98.0/24", "188.114.99.0/24"],
                ["162.159.192.0/24", "162.159.193.0/24", "162.159.195.0/24"]]
    index = 0
    if conf and RULES:  # 读取到的内容合法，才执行下面的步骤
        for cidrs in cidrs_li:
            index += 1
            ips = []
            for cidr in cidrs:
                ips.extend({str(ip) for ip in generate_ips_from_cidr(cidr)})  # 使用集合，打乱生成IP的顺序
            node_names = []
            node_li = ["proxies:\n", ]
            for server in ips:
                name = f"{server}:{port}"
                conf["name"] = name
                conf["server"] = server
                conf["port"] = port
                node_names.append(name)
                node_info_str = "  - {}\n".format(str(conf).replace(": True", ": true").replace(": False", ": false"))
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
            with open("warp-clash{}.yaml".format(index), mode="w", encoding="utf-8") as wf:
                wf.write(clash_content)
