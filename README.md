# 🎥 FullScreenTrack

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

[🌎 English](README.md) | [🀄 简体中文](README_zh.md)

</div>

## ✨ Highlights

- 🎬 Screen recording
- 🔊 Aaudio recording
- 🌩️ WebDAV cloud sync
- 🎨 Modern Material Design interface
- 🖥️ Seamless multi-monitor support
- 📊 File management
- 🔒 Customized storage mode

## 📸 Gallery

<div align="center">

### 🖥️ Clean Interface
<img src="./resources/example1.png" width="600" />

### 🔗 Functional File Management
<img src="./resources/example2.png" width="600" />

### ⚙️ Configable
<img src="./resources/example4.png" width="600" />

### 📊 Colorized Log Viewer
<img src="./resources/example3.png" width="600" />


</div>

## 🏗️ System Architecture

```mermaid
graph TD
    subgraph app
        A[GUI Interface]
        B[AppController]
    end

    subgraph core
        C[RecorderManager]
        D[LocalFileManager]
        E[UploaderManager]
        F[Screen Recorder]
        G[Audio Recorder]
        K[FFmpeg]
        I[WebDAVClient]
        H[File Model]

        subgraph Local Storage
            L[Local Storage]
            DB[(SQlite)]
        end

        subgraph Remote Storage
            J[WebDAV Server]
        end
    end


    A[GUI Interface] --> B[AppController]
    B --> C[RecorderManager]
    B --> D[LocalFileManager]
    B --> E[UploaderManager]
    C --> F[Screen Recorder]
    C --> G[Audio Recorder]
    D --> H[File Model]
    H --> DB[(SQlite)]
    E --> I[WebDAVClient]
    I --> J[WebDAV Server]
    F --> K[FFmpeg]
    G --> K
    K --> L[Local Storage]
    D --> L
    L --> E
    
```

## 💻 Tech Stack

```mermaid
mindmap
  root((🚀 FullScreenTrack))
    UI Layer 🎨
      PyQt5
      Material Design
    Core Engine ⚙️
      FFmpeg
      Screen Capture
      Audio Processing
    Storage System 💾
      WebDAV Client
      Local Cache
      SQLite Database
    Utils 🛠️
      Logging System
      Error Handling
```

## 📦 Quick Start

🔗 Download the latest release:
[Release Page](https://github.com/JeffZuo953/full-screen-track/releases)

### 🚀 Run from Release
1. Download the latest release from [Release Page](https://github.com/JeffZuo953/full-screen-track/releases)
2. Extract the zip file
3. Run `FullScreenTrack.exe`

### 🛠️ Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run with hot reload
python main.py
```

## 🔄 Workflow

```mermaid
sequenceDiagram
    participant UI as User Interface
    participant FM as File Monitor
    participant LF as Local Files
    participant UC as Upload Controller
    participant WD as WebDAV Client
    participant DB as Database

    activate FM
    loop Some seconds
        FM->>LF: Check for new files
        LF-->>FM: Return file list
        
        loop For each new file
            FM->>DB: Check file status
            DB-->>FM: Return status
            
            alt File not uploaded
                FM->>UC: Request upload
                UC->>WD: Upload file
                
                alt Upload successful
                    WD-->>UC: Upload complete
                    UC->>DB: Update status
                    UC-->>UI: Notify success
                else Upload failed
                    WD-->>UC: Upload failed
                    UC->>DB: Mark for retry
                    UC-->>UI: Show error
                end
            end
        end
    end
    deactivate FM
```
## ⚡ Data Flow Architecture

```mermaid
flowchart TB
    subgraph Input
        SC[Screen Capture]
        AC[Audio Capture]
    end

    subgraph Processing
        LF[Local File]
    end

    subgraph Local Storage
        F[File Model]
    end

    subgraph Remote Storage
        WD[WebDAV]
    end

    SC --> LF
    AC --> LF
    LF --> F
    F --> WD
```

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=JeffZuo953/full-screen-track&type=Date)](https://star-history.com/#JeffZuo953/full-screen-track&Date)

## 📄 License

This project is protected under the Apache License 2.0 - See [LICENSE](LICENSE) for details.

## 👥 Contributors

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/JeffZuo953">
        <img src="https://avatars.githubusercontent.com/u/JeffZuo953" width="100px;" alt=""/>
        <br />
        <sub><b>Jeff Zuo</b></sub>
      </a>
      <br />
      <sub>🎯 Project Lead</sub>
    </td>
  </tr>
</table>

## 📬 Get in Touch

- 📧 Email: jeffordszuo@gmail.com
- 🐱 GitHub: [@JeffZuo953](https://github.com/JeffZuo953)


<div align="center">

🌟 Made with ❤️ by Jeff Zuo 🌟

</div>