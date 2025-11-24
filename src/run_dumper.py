import os
import sys
import subprocess
import tempfile
import shutil

def find_lua_executable():
    for cmd in ["lua5.1", "lua", "luajit"]:
        path = shutil.which(cmd)
        if path:
            return path
    return None

def run_dumper(target_path, tools_dir):
    lua_exec = find_lua_executable()
    if not lua_exec:
        print("Error: No Lua interpreter found. Please install lua5.1, lua, or luajit.")
        sys.exit(1)
    
    print(f"Using Lua interpreter: {lua_exec}")

    dumper_template_path = os.path.join(tools_dir, "dumper.lua")
    if not os.path.exists(dumper_template_path):
        print(f"Error: {dumper_template_path} not found.")
        return


    with open(dumper_template_path, 'rb') as f:
        template = f.read()

    files = []
    if os.path.isfile(target_path):
        files.append(target_path)
        base_dir = os.path.dirname(target_path)
    elif os.path.isdir(target_path):
        base_dir = target_path
        files = [os.path.join(base_dir, f) for f in os.listdir(target_path) if f.endswith(".lua")]
        files.sort()
    else:
        print(f"Error: {target_path} is not a file or directory.")
        return

    if not files:
        print(f"No .lua files found in {target_path}")
        return

    print(f"Found {len(files)} lua file(s). Processing...")

    placeholder = b"-- PASTE YOUR OBFUSCATED SCRIPT HERE --"

    for fpath in files:
        fname = os.path.basename(fpath)
        print(f"--- Processing {fname} ---")
        

        with open(fpath, 'rb') as f:
            obfuscated_content = f.read()
        

        level = 0
        while True:
            eq = b"=" * level

            start_delim = b"[" + eq + b"["
            end_delim = b"]" + eq + b"]"
            if end_delim not in obfuscated_content:
                break
            level += 1
            
        match_start = template.find(b"local OBFUSCATED_SCRIPT =")
        if match_start == -1:
            print("Template structure unexpected. Could not find OBFUSCATED_SCRIPT.")
            continue
            
        ph_start = template.find(placeholder)
        if ph_start == -1:
            print("Template structure unexpected. Could not find placeholder.")
            continue
            
        if b"]]" not in obfuscated_content:

            final_script = template.replace(placeholder, obfuscated_content)
        else:

            open_bracket_pos = template.rfind(b"[[", 0, ph_start)
            close_bracket_pos = template.find(b"]]", ph_start)
            
            if open_bracket_pos == -1 or close_bracket_pos == -1:
                print("Could not find delimiters in template.")
                continue
                
            part1 = template[:open_bracket_pos]
            part2 = template[close_bracket_pos+2:]
            
            final_script = part1 + start_delim + b"\n" + obfuscated_content + b"\n" + end_delim + part2


        with tempfile.NamedTemporaryFile(mode='wb', suffix='.lua', delete=False) as tmp:
            tmp.write(final_script)
            tmp_path = tmp.name
        
        try:
            result = subprocess.run([lua_exec, tmp_path], capture_output=True)
            
            stdout = result.stdout.decode('utf-8', errors='replace')
            stderr = result.stderr.decode('utf-8', errors='replace')
            
            dumped_lines = []
            for line in stdout.splitlines():
                if "[DUMP]" in line:
                    print(line.replace("[DUMP] ", ""))
                    dumped_lines.append(line)
            
            if stderr:
                 if "Error" in stderr or "stack traceback" in stderr:
                     print(f"Error output: {stderr}")
            
            if not dumped_lines and not stderr:
                print("(No SetCore calls intercepted)")
                
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        
        print("\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 run_dumper.py <obfuscated_file_or_dir>")
    else:
        tools_dir = os.path.dirname(os.path.abspath(__file__))
        run_dumper(sys.argv[1], tools_dir)
