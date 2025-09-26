# CipherStorm
Pedator Database Manager
</br>
NOT FOR THE PUBLIC

# Setup
## Windows
XAMPP is used solely for the purpose of starting MySQL. If you perfer to use another method for starting MySQL, go ahead but do not submit any issues or PRs if any part of the setup does not work.

- Download the source code ZIP from the releases or ``git clone`` this repo
- Install [XAMPP](https://www.apachefriends.org/)
- Launch the XAMPP Control Panel
- Start MySQL
- Now launch the start.bat file
-----
Congrats you have cipherstorm running!

## Linux
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
```
Now run the start.sh file by
```bash
chmod +x start.sh
./start.sh
```
if your done with using cipherstorm you can stop the mysql instance by
```bash
sudo systemctl stop mysql
```
removing it to auto-start on boot
```bash
sudo systemctl disable mysql
```

# Login info
- USER: admin
- PASS: admin123
