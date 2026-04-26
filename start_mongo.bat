@echo off
set MONGO_BIN=h:\My Major Project\mongodb_bin\mongodb-win32-x86_64-windows-7.0.2\bin
set MONGO_DATA=h:\My Major Project\mongo_data_clean
if not exist "%MONGO_DATA%" mkdir "%MONGO_DATA%"
"%MONGO_BIN%\mongod.exe" --dbpath "%MONGO_DATA%" --port 27017 --bind_ip 127.0.0.1
