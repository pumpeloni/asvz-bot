# ASVZ ENROLLMENT BOT
A bot for Raspberry Pi OS that enrolls you into ASVZ courses

# Installation
### The installation and the bot needs these packages
- python3
- python3 pip
- virtualenv
- chromium
- chromium-chromedriver
- git

### Instructions
```
cd
git clone https://github.com/pumpeloni/asvz-bot.git
cd asvz-bot/asvz_bot/files
python3 -m pip install virtualenv
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 asvz_bot_c.py -h
```
# Run
### Run the bot manually
```
cd asvz-bot/asvz_bot/files
source .venv/bin/activate
python3 asvz_bot_c.py [all the requiered informations like login etc. (see "-h" or the example below)]
```
#### Example
Irchel - Fitness, Monday at 18:25 in Irchel Sport Center
```
python3 asvz_bot_c.py -u  maxmuster -p MusterWort -w 0 -t 18:25 -e 24 -f 'Sport Center Irchel' 'https://www.asvz.ch/426-sportfahrplan?f[0]=sport:122920'
```
### Run bot automatically
to use the bot automatically use crontab like discribed below
1. copy tempalte.sh and fill in your credentials as in the file described
2. save it, rename it and copy the path
3. create cronjob like this:
```
crontab -e
# enter new line:
min hour * * day bash [enter copied path]
# example for lesson that the start of enrolment is at 18:00
00 17 * * 3 bash /home/pi/asvz-bot/jobs/beachvolley_1.sh
