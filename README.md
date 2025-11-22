# WeAreDevs Lua Deobfuscator

A toolkit for analyzing and deobfuscating Lua scripts protected by the WeAreDevs obfuscator (v1.0.0).

## Overview

This project provides tools to dynamically analyze obfuscated Lua scripts by running them in a mocked Roblox/Exploit environment. It intercepts key function calls (like `loadstring`, `game:GetService`, `table.concat`) to reveal the underlying logic and payloads.

## Tools

### 1. Dynamic Dumper (`tools/run_dumper.py`)
The primary tool. It wraps the obfuscated script in a Lua environment mock (`tools/dumper.lua`) and executes it using Lua 5.1.

**Features:**
- Mocks Roblox Globals: `game`, `workspace`, `script`, `Instance`, `Vector3`, `CFrame`, `Drawing`, etc.
- Mocks Exploit Environment: `getgenv`, `checkcaller`, `identifyexecutor`.
- Logging: Captures `print`, `warn`, `SetCore` notifications, and `loadstring` content.
- Robustness: Handles complex obfuscation techniques involving string shuffling and proxy objects.

### 2. Static Extractor (`tools/extract_strings.py`)
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

### Running the Dumper

To analyze a single obfuscated file:
```bash
python3 tools/run_dumper.py path/to/obfuscated_script.lua
```

To analyze a directory of scripts:
```bash
python3 tools/run_dumper.py path/to/folder/
```

The tool will output the execution logs, including:
- `[DUMP] ...`: Intercepted calls and values.
- `LOADSTRING CONTENT`: The code being dynamically loaded (the payload).
- `TABLE.CONCAT LARGE STRING`: Potential encrypted payloads being built.

### Example Output

```
[DUMP] game.StarterGui:SetCore("SendNotification", { ... })
[DUMP] LOADSTRING DETECTED (len=1024)
[DUMP] LOADSTRING CONTENT: print("Hello World")
```

## Status

- **Basic/Hard Scripts**: Supported. The dumper successfully runs these scripts and captures notifications and string construction.
- **Extreme Scripts**: Experimental. Some highly obfuscated scripts may crash due to sensitive anti-tamper checks or complex VM logic.

## Documentation

See [docs/DEOBFUSCATION_NOTES.md](docs/DEOBFUSCATION_NOTES.md) for detailed analysis notes.
