# Debugging the Deobfuscator

## Progression Info & Debugging Steps

This document outlines the changes made to the deobfuscator to handle "Wearedevs" / "Prometheus" obfuscation and provides guidance on debugging future issues.

### Obfuscation Analysis
The targeted scripts use "Prometheus" obfuscation, which features:
1.  **Virtualization:** A custom VM that interprets bytecode.
2.  **Anti-Tamper / Anti-Analysis:**
    -   Checks for the existence of global tables (`getfenv`, `_ENV`).
    -   Checks for `newproxy` and `userdata` types.
    -   Checks if environment tables are read-only or contain specific keys.
    -   Uses "ProxifyLocals" to wrap local variables in tables with metamethods (`__index`, `__newindex`, `__concat`).
3.  **String Encryption:** Strings are encrypted and decrypted at runtime using arithmetic operations.
4.  **Control Flow Flattening:** The code structure is flattened into a loop.

### Recent Changes & Fixes

1.  **Timeout Issues:**
    -   **Problem:** The decryption loops in Prometheus are computationally expensive and were triggering the 30-second timeout in the Python runner and the 5-second debug hook in the Lua dumper.
    -   **Fix:**
        -   Increased Python `subprocess` timeout to **120 seconds**.
        -   Disabled the Lua `debug.sethook` timeout mechanism entirely in `src/dumper.lua` to allow long-running decryption.

2.  **Anti-Tamper & Environment Security:**
    -   **Problem:** The scripts check for the presence of standard Lua libraries (`math`, `string`, etc.) and specific behavior of `getfenv`. Strict sandboxing (removing `os`, `io`) caused these checks to fail, leading to crashes or infinite loops.
    -   **Fix:**
        -   **Full Environment Access:** We now populate `MockEnv` with *all* globals from the real Lua 5.1 environment (`RealEnv`), including `os`, `io`, `package`, etc. This satisfies the obfuscator's integrity checks.
        -   **WARNING:** This allows the obfuscated script to execute system commands. Run only in a disposable sandbox (like this environment).

3.  **Concatenation & Type Errors:**
    -   **Problem:** `attempt to concatenate local 'Z' (a table value)` and `table expected, got userdata`.
    -   **Fix:**
        -   **MockEnv Metamethods:** Added `__concat` and `__tostring` to `MockEnv`'s metatable so it behaves gracefully if concatenated.
        -   **Proxy Implementation:** Changed `CreateProxy` to return a `table` instead of `newproxy` (userdata). This ensures compatibility with Lua 5.1's `__concat` when mixed with other tables (since Prometheus wraps locals in tables).

### How to Proceed with Debugging

If a new script fails to deobfuscate (crashes or returns nothing):

1.  **Check the Logs:**
    -   Run the dumper: `python3 src/deobfuscator_console.py path/to/script.lua output.lua decompile`
    -   Look for `[DUMP]` lines or `Lua Error`.
    -   **"MISSING GLOBAL":** This means the script tried to access a global that isn't in `MockEnv` or `RealEnv`. You may need to mock it in `src/dumper.lua`.
    -   **"FALLBACK TO REALENV":** This confirms the dumper is using the real environment for an unknown global.

2.  **Common Errors:**
    -   `attempt to concatenate ...`:
        -   The script is trying to concatenate a proxy object. Ensure `CreateProxy` returns a table with `__concat` (currently implemented).
        -   If it's `MockEnv` being concatenated, check `setmetatable(MockEnv, ...)`.
    -   `timeout`:
        -   If it still times out, increase the timeout in `src/deobfuscator_console.py`.
    -   `bad argument #1 to 'x' (table expected, got userdata)`:
        -   Prometheus expects `table` types for its proxies. Ensure `CreateProxy` returns a table.

3.  **Isolating the Crash:**
    -   Use `print` debugging in `src/dumper.lua` inside `CreateProxy` or the main execution block to see where it stops.
    -   If the script detects tampering, it might silently fail or loop forever.

### Security Note
The current configuration **disables security restrictions** to ensure compatibility. Do not run unknown obfuscated scripts on your personal machine without isolation (VM/Docker).
