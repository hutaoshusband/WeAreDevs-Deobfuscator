# ⚠️ DISCLAIMER: NO UPDATES / NO SUPPORT ⚠️

**READ THIS BEFORE USING OR DOWNLOADING:**

**I DO NOT GIVE UPDATES FOR THIS DEOBFUSCATOR.**
**I DO NOT PROVIDE SUPPORT FOR THIS DEOBFUSCATOR.**

This project is **ARCHIVED** and provided **"AS-IS"**. 

*   If the tool does not work for your specific script: **I will not fix it.**
*   If you encounter a bug: **I will not fix it.**
*   If you don't know how to use it: **I will not help you.**

I am not the developer of the obfuscator itself. I created this tool for a specific use case, and I am sharing it as open source. **We are not responsible if this Open Source Tool does not work correctly.**

**If it does not work, FIX IT YOURSELF.** Clone the repository and modify the code. Do not ask for help on Discord or GitHub issues expecting a fix from me. I do not have the time to maintain this project or provide technical support.

---

# WeAreDevs Lua Deobfuscator / Prometheus Deobfuscator

A toolkit for analyzing and deobfuscating Lua scripts protected by the WeAreDevs obfuscator (v1.0.0).

## Overview

This project provides tools to dynamically analyze obfuscated Lua scripts by running them in a mocked Roblox/Exploit environment. It intercepts key function calls (like `loadstring`, `game:GetService`, `table.concat`) to reveal the underlying logic and payloads.

## Tools

### 1. Dynamic Dumper (`src/deobfuscator_console.py`)
The primary tool. It wraps the obfuscated script in a Lua environment mock (`src/dumper.lua`) and executes it using Lua 5.1.

**Features:**
- Mocks Roblox Globals: `game`, `workspace`, `script`, `Instance`, `Vector3`, `CFrame`, `Drawing`, etc.
- Mocks Exploit Environment: `getgenv`, `checkcaller`, `identifyexecutor`.
- Logging: Captures `print`, `warn`, `SetCore` notifications, and `loadstring` content.
- Robustness: Handles complex obfuscation techniques involving string shuffling and proxy objects.

### 2. Static Extractor (`src/extract_strings.py`)
Attempts to statically extract encrypted strings from the script file.

## Prerequisites

- **Lua 5.1**: Required to run the dumper.
  - Ubuntu/Debian: `sudo apt install lua5.1`
  - MacOS: `brew install lua@5.1`
  - Windows: Download from [LuaBinaries](http://luabinaries.sourceforge.net/) or place `lua.exe` next to the deobfuscator executable

## Installation

### Option 1: Pre-built Binary (Windows)

Download the latest pre-built `deobfuscator.exe` from the [Releases](https://github.com/HUTAOSHUSBAND/WeAreDevs-Deobfuscator/releases) page.

**Requirements:**
- Place `lua.exe` (Lua 5.1) in the same folder as `deobfuscator.exe`, or have it in your system PATH

**Usage:**
1. Run `deobfuscator.exe`
2. Drag and drop your obfuscated `.lua` file into the console
3. The deobfuscated output will be saved as `filename_deobfuscated.lua`

### Option 2: Run from Source

Clone the repository and use the Python tools directly (see Usage section below).

## Usage

### Running the Console Tool

To analyze a single obfuscated file using the console tool:
```bash
python3 src/deobfuscator_console.py path/to/obfuscated_script.lua output_path.lua decompile
```

The tool will output the execution logs and save the deobfuscated content to the output path.

### Example Output

```
[DUMP] game.StarterGui:SetCore("SendNotification", { ... })
[DUMP] LOADSTRING DETECTED (len=1024)
[DUMP] LOADSTRING CONTENT: print("Hello World")
```

## Status

- **Basic/Hard Scripts**: Supported. The dumper successfully runs these scripts and captures notifications and string construction.
- **Extreme Scripts**: Supported (Experimental). Uses a hybrid extraction method to recover decrypted strings at runtime.

## Documentation

See [docs/DEOBFUSCATION_NOTES.md](docs/DEOBFUSCATION_NOTES.md) for detailed analysis notes.

---

**REMINDER: NO UPDATES. NO SUPPORT. FIX IT YOURSELF.**
