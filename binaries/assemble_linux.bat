@echo off
copy /b linux_chunks\chunk_aa + linux_chunks\chunk_ab + linux_chunks\chunk_ac + linux_chunks\chunk_ad deobfuscator_linux
echo Reassembled deobfuscator_linux
pause
