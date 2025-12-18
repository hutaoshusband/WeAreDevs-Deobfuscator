import os
import sys
import subprocess
import tempfile
import shutil
import time
import argparse
try:
    import winsound
except ImportError:
    winsound = None
import base64

# Import the string extractor
try:
    from extract_strings import get_decrypted_strings
except ImportError:
    # Handle cases where run from a different directory or PyInstaller
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from extract_strings import get_decrypted_strings

_a1 = base64.b64decode(b'TWFkZSBieQ==').decode()
_a2 = base64.b64decode(b'SFVUQU9TSFVTQkFORA==').decode()
_a3 = lambda: f"{_a1} {_a2}"
_verify_attr = lambda s: _a2.lower() in s.lower()

def beep():
    # Non-interactive, so we don't need beeps.
    pass

def find_lua_executable():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
        local_lua = os.path.join(base_path, "lua.exe")
        if os.path.exists(local_lua): return local_lua
        
    for cmd in ["lua5.1", "lua", "luajit"]:
        path = shutil.which(cmd)
        if path:
            return path
    return None

def main():
    parser = argparse.ArgumentParser(description="WeAreDevs Deobfuscator - Command Line Interface")
    parser.add_argument("input", help="Path to the input .lua file")
    parser.add_argument("output", help="Path to save the deobfuscated output")
    parser.add_argument("mode", choices=['dump', 'decompile'], help="The deobfuscation mode to use ('dump' or 'decompile')")
    
    args = parser.parse_args()
    
    target_path = args.input
    output_path = args.output
    choice = '1' if args.mode == 'dump' else '2'

    if not os.path.exists(target_path):
        print("FATAL: File not found!", file=sys.stderr)
        sys.exit(1)

    try:
        with open(target_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if "FireflyProtect" in content:
                print("We cannot deobfuscate FireflyProtector.", file=sys.stderr)
                sys.exit(1)
    except Exception as e:
        print(f"FATAL: Could not read input file: {e}", file=sys.stderr)
        sys.exit(1)

    if choice == '1':
        # Dump Constants Mode
        print("Processing strings...")
        try:
            with open(target_path, 'r', encoding='latin1') as f:
                content = f.read()
            
            decrypted = get_decrypted_strings(content)
            
            if decrypted:
                with open(output_path, 'w', encoding='utf-8') as out_f:
                    for s in decrypted:
                        out_f.write(s + '\n')
                print(f"Dump complete. Saved to {output_path}")
            else:
                print("No strings found or decryption failed.")
                with open(output_path, 'w', encoding='utf-8') as out_f:
                    out_f.write("-- No strings found or decryption failed --")
            
        except Exception as e:
            print(f"FATAL: Error processing strings: {e}", file=sys.stderr)
            sys.exit(1)
            
    elif choice == '2':
        # Deobfuscate Mode (Existing Logic)
        lua_exec = find_lua_executable()
        if not lua_exec:
            print("FATAL: No Lua interpreter found. Please install lua5.1, lua, or luajit.", file=sys.stderr)
            sys.exit(1)
        
        print(f"Using Lua interpreter: {lua_exec}")

        tools_dir = os.path.dirname(os.path.abspath(__file__))
        dumper_path = os.path.join(tools_dir, 'dumper.lua')

        if not os.path.exists(dumper_path):
             print(f"FATAL: dumper.lua not found at {dumper_path}", file=sys.stderr)
             sys.exit(1)

        try:
            with open(dumper_path, 'rb') as f:
                template = f.read()
        except Exception as e:
            print(f"FATAL: Error reading dumper template: {e}", file=sys.stderr)
            sys.exit(1)

        try:
            with open(target_path, 'rb') as f:
                obfuscated_content = f.read()
        except Exception as e:
            print(f"FATAL: Error reading file: {e}", file=sys.stderr)
            sys.exit(1)

        placeholder = b"-- PASTE YOUR OBFUSCATED SCRIPT HERE --"
        
        level = 0
        while True:
            eq = b"=" * level
            start_delim = b"[" + eq + b"["
            end_delim = b"]" + eq + b"]"
            if end_delim not in obfuscated_content:
                break
            level += 1
            
        ph_start = template.find(placeholder)
        
        if ph_start == -1:
            print("FATAL: Internal Error: Template structure corrupted.", file=sys.stderr)
            sys.exit(1)

        open_bracket_pos = template.rfind(b"[[", 0, ph_start)
        close_bracket_pos = template.find(b"]]", ph_start)
        
        if open_bracket_pos == -1 or close_bracket_pos == -1:
            print("FATAL: Internal Error: Could not find delimiters in template.", file=sys.stderr)
            sys.exit(1)
            
        part1 = template[:open_bracket_pos]
        part2 = template[close_bracket_pos+2:]
        
        final_script = part1 + start_delim + b"\n" + obfuscated_content + b"\n" + end_delim + part2

        with tempfile.NamedTemporaryFile(mode='wb', suffix='.lua', delete=False) as tmp:
            tmp.write(final_script)
            tmp_path = tmp.name
        
        try:
            print("Executing dynamic analysis with Lua...")
            result = subprocess.run([lua_exec, tmp_path], capture_output=True, timeout=120)
            
            stdout = result.stdout.decode('utf-8', errors='replace')
            stderr = result.stderr.decode('utf-8', errors='replace')
            
            dumped_lines = [line.replace("[DUMP] ", "") for line in stdout.splitlines() if "[DUMP]" in line]
            
            if stderr and ("Error" in stderr or "stack traceback" in stderr):
                 print(f"Lua Error: {stderr}", file=sys.stderr)
            
            if dumped_lines:
                with open(output_path, 'w', encoding='utf-8') as out_f:
                    out_f.write("\n".join(dumped_lines))
                print(f"Deobfuscation successful. Saved to {output_path}")
            else:
                print("No deobfuscated content found.")
                with open(output_path, 'w', encoding='utf-8') as out_f:
                    out_f.write("-- No dynamic output was captured --")
                
        except subprocess.TimeoutExpired:
            print("FATAL: Lua script execution timed out after 120 seconds.", file=sys.stderr)
            sys.exit(1)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    else:
        print("FATAL: Invalid mode selected.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
