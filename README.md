
<p align="center">
    <img src="https://github.com/Glitchy-Sheep/handbrake-batch-compressor/blob/main/assets/banner.png?raw=true" style="width: 80%; "/>
</p>

# 🖥️ About

Welcome to the **HandbrakeCLI Batch Compressor** project! 

This application is designed to **compress video files** in bulk using the **HandbrakeCLI**.
It offers many [features](#-features) to customize the compression process such as:
- *deletion of original files*
- *show statistics during and after the compression*
- *smart filtering and skipping of files based on your specified rules (see usage)*


## 📑 Table of Contents
- [🖥️ About](#️-about)
  - [📑 Table of Contents](#-table-of-contents)
  - [✨ Features](#-features)
  - [📸 Screenshots](#-screenshots)
  - [🛠️ Installation](#️-installation)
  - [🚀 Usage and Examples](#-usage-and-examples)
    - [⚙️ Advanced Usage](#️-advanced-usage)
  - [🧠 Smart Filters](#-smart-filters)
  - [📜 License](#-license)



## ✨ Features

- **Bulk Compression**: Compress multiple video files at once using HandbrakeCLI.
- **Custom Compression Options**: Pass any options available in HandbrakeCLI, like encoders and quality settings.
- **File Management**: Automatically detect compressed and incomplete files if your process is interrupted.
- **Filter Features**: Smart filters allow skipping videos that don't meet your criteria (e.g., resolution, bitrate, or frame rate).
- **Statistics**: Optionally display compression stats during and after the process.
- **Replace Original Files**: Automatically delete original files if they are successfully compressed.
- **Automatic Installation**: Automatically install HandbrakeCLI and dependencies if not already installed.

## 📸 Screenshots

<img src="https://raw.githubusercontent.com/Glitchy-Sheep/handbrake-batch-compressor/refs/heads/feature/simplify-cli-options/assets/compressing-example-1.png" style="width: 100%; "/>

<img src="https://raw.githubusercontent.com/Glitchy-Sheep/handbrake-batch-compressor/refs/heads/feature/simplify-cli-options/assets/compressing-example-2.png" style="width: 100%; "/>

## 🛠️ Installation

1. **Install python**:
   - Window:
      ```bash
      winget install Python.Python.3.12
      ```
   - Linux:
      ```bash
      sudo apt-get install python3
      ```
   - macOS:
      ```bash
      brew install python
      ```

2. **Install the handbrake-batch-compressor package:**
   ```bash
   pip install handbrake-batch-compressor
   ```

3. **Run the application:**
   ```bash
   handbrake-batch-compressor --help
   ```


## 🚀 Usage and Examples

**Highly recommended** to see both `--help` and `--guide` before compression.

<img src="https://raw.githubusercontent.com/Glitchy-Sheep/handbrake-batch-compressor/refs/heads/feature/simplify-cli-options/assets/usage.png" style="width: 100%; "/>

### ⚙️ Advanced Usage

You can specify more options such as HandbrakeCLI settings, file extensions, and whether to delete the originals after processing.

```bash
python main.py -t ./videos -o "--encoder x264 --quality 20" \
    --progress-extension c \
    --complete-extension x \
    --show-stats \
    --effective-compression-behavior delete_original \
    --ineffective-compression-behavior delete_compressed
```

## 🧠 Smart Filters

Smart filters allow you to apply conditions that control which videos will be processed based on their characteristics.

- **Minimum Bitrate**: Skips videos with a bitrate lower than the specified value.
- **Minimum Frame Rate**: Skips videos with a frame rate lower than the specified value.
- **Minimum Resolution**: Skips videos with a resolution lower than the specified threshold.

These filters help avoid unnecessary processing of low-quality videos.


## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
