将代码下载或git clone到本地电脑中，然后按下面的步骤操作：

#### 一、安装Python和PyYAML第三方库（懂的人就忽略）

1. **下载Python安装包**：
   访问Python的官方网站（https://www.python.org/downloads/ ），选择适用于您操作系统的Python版本进行下载。一般来说，Linux和macOS系统会使用.tar.xz格式的包，而Windows系统则会使用.exe安装程序。

2. **安装Python**：

   - 对于Windows系统，运行下载的.exe安装程序，按照提示完成安装。安装时建议将Python添加到系统环境变量中，这样可以在任何命令行界面中直接使用Python。
   - 对于macOS系统，下载.tar.xz包后，解压到指定目录，然后可以通过终端使用`python3`命令来调用Python。
   - 对于Linux系统，也是下载.tar.xz包后，解压到指定目录，然后可以通过终端使用`python3`命令来调用Python。

3. **验证安装**：
   打开命令行工具（在Windows中是cmd或PowerShell，macOS和Linux中是Terminal），输入`python`（或者`python3`），如果能够进入Python的交互式环境，则说明Python安装成功。

4. **安装必要的PyYAML库**：
   你可以使用 pip 来安装 PyYAML。在命令行中运行以下命令：

   ```bash
   pip install PyYAML
   ```

    如果你使用的是 Linux 或 macOS 系统，可能需要使用 `pip3` 命令来确保为 Python3 安装 PyYAML：

   ```bash
   pip3 install PyYAML
   ```

#### 二、修改 [resources/wg_config.yaml ](https://github.com/juerson/wrap_wireguard_convert_clash.meta/blob/master/resources/wireguard-config.yaml)里面的配置信息

```
name: "wg-warp"
type: wireguard
private-key: OOrigZsSjw2YaY4urjbbU4/BNOZKXqW6EYNm8XKLtkU=  # 这里修改成你的PrivateKey
server: 162.159.192.1
port: ""  # 这里的端口为空或不是WARP UDP端口的，程序会随机选择一个端口
ip: 172.16.0.2  # 注意没有后面的"/32"
ipv6: 2606:4700:110:82ce:bdeb:e72d:572a:e280  # 这里修改成的你的ipv6 Address，注意没有后面的"/128"
public-key: bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo=  # 这里warp的PublicKey都是相同的
# reserved: [209,98,59]  # 可选参数，字符串格式也是合法的，如"U4An"
udp: true
```

注：本配置的信息，参考了[这个网站](https://wiki.metacubex.one/config/proxies/wg/)

#### 三、windows中双击`run.bat`文件或执行`python main.py`命令运行

#### 四、生成`warp-clash.yaml`文件就是你需要的clash配置文件，导入 [clash verge](https://github.com/clash-verge-rev/clash-verge-rev) 或绝版 [clash_for_windows_pkg](https://archive.org/download/clash_for_windows_pkg) 使用即可。

注意：原来的`clash_for_windows_pkg`软件，貌似不支持`wriegroud`协议的节点，需要将clash内核换成[clash.meta](https://github.com/MetaCubeX/mihomo/releases/tag/v1.16.0)的内核，才支持`wiregroud`协议的节点。

大概路径在`Clash.for.Windows-0.20.39-win\resources\static\files\win\x64`下的`clash-win64.exe`程序换成 [clash.meta](https://github.com/MetaCubeX/mihomo/releases/download/v1.16.0/clash.meta-windows-amd64-cgo-v1.16.0.zip) 的。(这个你会吧，就是把 [clash.meta](https://github.com/MetaCubeX/mihomo/releases/download/v1.16.0/clash.meta-windows-amd64-cgo-v1.16.0.zip) 的内核下载下来，解压重命名为`clash-win64.exe`，然后复制/剪切到前面提到的路径中，把原来的`clash-win64.exe`程序替换掉，重启`Clash for Windows`)

由于[clash verge](https://github.com/clash-verge-rev/clash-verge-rev) 新开发，可能会出现延迟超时、无法上网等问题，不知道是`clash verge`软件中内置的`clash.meta`更名`mihomo`内核问题，还是`clash verge`客户端问题。

推荐使用 [clash_for_windows_pkg](https://archive.org/download/clash_for_windows_pkg) + [clash.meta v1.16.0 内核](https://github.com/MetaCubeX/mihomo/releases/download/v1.16.0/clash.meta-windows-amd64-cgo-v1.16.0.zip) ，如果英文界面使用不方便，可以使用[Clash for Windows V0.20.39 汉化版](https://github.com/Z-Siqi/Clash-for-Windows_Chinese/releases/tag/CFW-V0.20.39_CN)，貌似不用更换内核，使用原来的`Clash Premium`内核，是支持`wireguard`协议的 Clash 配置文件。
