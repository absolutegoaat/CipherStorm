# CipherStorm
People database mainly used for catching criminals and storing descriptions of who and what they are, This is used to store predators, racist, terrorists, and other people who are dangerous to society or online safety.

CipherStorm makes it easy to look back at the information you've stored and find the information you need at a moment's notice.

# Features
- MySQL database
- Stores Names, Addresses, Phone Numbers, Descriptions, IP Addresses, Conviction, and labels to quickly describe someone with one word. (More to come)
- Stores images
- An API for developers who want to use CipherStorm with out the hassle of getting MySQL Credentials from an Administrator.
- Easy to use
- Easy to setup

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

# Docker
```docker-compose up --build```
> [!NOTE]
> CipherStorm may start without mysql starting up, wait until mysql is done and listening for connections and then start
> CipherStorm by ```docker start cipherstorm```

# Login info
- USER: admin
- PASS: admin123

# Issues
If you have any issues, don't hessitate to open an issue, And i'll or someone will get to you to help you out.

# Contributing
If you want to contribute, feel free to fork this project and open a PR, and i'll review it and merge it if it's good.