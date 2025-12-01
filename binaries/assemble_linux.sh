#!/bin/bash
cat linux_chunks/chunk_* > deobfuscator_linux
chmod +x deobfuscator_linux
echo "Reassembled deobfuscator_linux"
