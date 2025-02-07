[🌎 English](README.md) | [🀄 简体中文](README_zh.md)

# 🤔 你是否遇到过这些情况？

- 📄 浏览器意外刷新，重要参考资料消失不见
- 🔍 找不到昨天查看过的文件或视频的位置
- ⚖️ 遇到劳动纠纷，需要可靠的工作记录证明
- 📊 月度考核时，难以量化工作成果
- 📝 远程会议结束后，遗漏重要细节
- 🎥 制作演示视频时，难以定位错误片段

## 😲 什么是 FullScreenTrack？

FullScreenTrack 是您的专业屏幕活动记录解决方案。它提供：

- 🎯 自动屏幕和音频录制
- 💾 智能本地存储管理
- ☁️ 安全云端同步
- 📊 全面活动日志
- 🔍 快速内容检索
- 🛡️ 数据备份保护


# 🎥 FullScreenTrack 全屏录制工具
<div align="center">

![FullScreenTrack](./resources/icon.ico)

[![GitHub license](https://img.shields.io/github/license/jeffzuo/full-screen-track)](https://github.com/jeffzuo/full-screen-track/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/PyQt-5.15+-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-4.0+-red.svg)](https://ffmpeg.org/)
[![Material Design](https://img.shields.io/badge/Material%20Design-Icons-purple.svg)](https://material.io/design)
[![SQLite](https://img.shields.io/badge/SQLite-3-blue.svg)](https://www.sqlite.org/)
[![Downloads](https://img.shields.io/github/downloads/jeffzuo/full-screen-track/total)](https://github.com/jeffzuo/full-screen-track/releases)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://makeapullrequest.com)


</div>


无论您是需要记录工作的专业人士，保持工作透明度的远程工作者，还是需要可靠屏幕录制的内容创作者 - FullScreenTrack 都能满足您的需求。

## ✨ 主要特性

- 🎬 专业的屏幕录制功能
- 🔊 高质量音频采集
- 🌩️ WebDAV云端同步
- 🎨 现代化Material Design界面
- 🖥️ 完善的多显示器支持
- 📊 智能文件管理系统
- 🔒 安全可靠的存储方案
- ⚡ 高性能低资源占用

## 📸 界面展示

<div align="center">

### 🖥️ 简洁的主界面
<img src="./resources/example1.png" width="600" />

### 🔗 功能完备的文件管理
<img src="./resources/example2.png" width="600" />

### ⚙️ 丰富的配置选项
<img src="./resources/example4.png" width="600" />

### 📊 彩色日志查看器
<img src="./resources/example3.png" width="600" />

</div>

## 🏗️ 系统架构

```mermaid
graph TD
    subgraph 应用层
        A[图形界面]
        B[应用控制器]
    end

    subgraph 核心层
        C[录制管理器]
        D[本地文件管理器]
        E[上传管理器]
        F[屏幕录制器]
        G[音频录制器]
        K[FFmpeg]
        I[WebDAV客户端]
        H[文件模型]

        subgraph 本地存储
            L[本地存储]
            DB[(数据库)]
        end

        subgraph 远程存储
            J[WebDAV服务器]
        end
    end

    A[图形界面] --> B[应用控制器]
    B --> C[录制管理器]
    B --> D[本地文件管理器]
    B --> E[上传管理器]
    C --> F[屏幕录制器]
    C --> G[音频录制器]
    D --> H[文件模型]
    H --> DB[(数据库)]
    E --> I[WebDAV客户端]
    I --> J[WebDAV服务器]
    F --> K[FFmpeg]
    G --> K
    K --> L[本地存储]
    D --> L
    L --> E
```

## 💻 技术栈

```mermaid
mindmap
  root((🚀 全屏录制))
    界面层 🎨
      PyQt5
      Material Design
    核心引擎 ⚙️
      FFmpeg
      屏幕捕获
      音频处理
    存储系统 💾
      WebDAV客户端
      本地缓存
      SQLite数据库
    工具集 🛠️
      日志系统
      错误处理
```

## 📦 快速开始

🔗 下载最新版本：
[下载页面](https://github.com/JeffZuo953/full-screen-track/releases)


### 🚀 运行发布版本
1. 从[发布页面](https://github.com/JeffZuo953/full-screen-track/releases)下载最新版本
2. 解压缩文件
3. 运行 `FullScreenTrack.exe`

### 🛠️ 开发环境配置
```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 使用热重载运行
python main.py
```


## 🔄 工作流程

```mermaid
sequenceDiagram
    participant UI as 用户界面
    participant FM as 文件监视器
    participant LF as 本地文件
    participant UC as 上传控制器
    participant WD as WebDAV客户端
    participant DB as 数据库

    activate FM
    loop 定时检查
        FM->>LF: 检查新文件
        LF-->>FM: 返回文件列表
        
        loop 对每个新文件
            FM->>DB: 检查文件状态
            DB-->>FM: 返回状态
            
            alt 文件未上传
                FM->>UC: 请求上传
                UC->>WD: 上传文件
                
                alt 上传成功
                    WD-->>UC: 上传完成
                    UC->>DB: 更新状态
                    UC-->>UI: 通知成功
                else 上传失败
                    WD-->>UC: 上传失败
                    UC->>DB: 标记重试
                    UC-->>UI: 显示错误
                end
            end
        end
    end
    deactivate FM
```

## ⚡ 数据流架构

```mermaid
flowchart TB
    subgraph 输入
        SC[屏幕捕获]
        AC[音频捕获]
    end

    subgraph 处理
        LF[本地文件]
    end

    subgraph 本地存储
        F[文件模型]
    end

    subgraph 远程存储
        WD[WebDAV]
    end

    SC --> LF
    AC --> LF
    LF --> F
    F --> WD
```

## ⭐ 项目活跃度

[![Star History Chart](https://api.star-history.com/svg?repos=JeffZuo953/full-screen-track&type=Date)](https://star-history.com/#JeffZuo953/full-screen-track&Date)


## 📄 开源协议

本项目采用 Apache License 2.0 协议 - 详情请查看 [LICENSE](LICENSE) 文件

## 👥 贡献者

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/JeffZuo953">
        <img src="https://avatars.githubusercontent.com/u/JeffZuo953" width="100px;" alt=""/>
        <br />
        <sub><b>Jeff Zuo</b></sub>
      </a>
      <br />
      <sub>🎯 项目负责人</sub>
    </td>
  </tr>
</table>

## 📬 联系方式

- 📧 邮箱: jeffordszuo@gmail.com
- 🐱 GitHub: [@JeffZuo953](https://github.com/JeffZuo953)

<div align="center">

🌟 由 Jeff Zuo 用 ❤️ 精心打造 🌟

</div>
