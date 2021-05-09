# --- Starts the bot ---
cd asvz-bot/asvz_bot/files
python3 -m venv .venv
source .venv/bin/activate

# --- Enter all needed informations here ---

python3 asvz_bot_c.py # enter infromation here

# --- HELP ---
# python3 asvz_bot_c.py -u [username] -p [password] -w [weekday, 0 = monday, 6 = sunday] -t [time hh:mm] -e [enrolment time difference] -f [facility] [link]

# --- Example --- 
# Irchel - Fitness, Monday at 18:25 in Irchel Sport Center
# python3 asvz_bot_c.py -u  maxmuster -p MusterWort -w 0 -t 18:25 -e 24 -f 'Sport Center Irchel' 'https://www.asvz.ch/426-sportfahrplan?f[0]=sport:122920&f[1]=facility:45577'

# --- Additional information

#  link                  link to particular sport on ASVZ Sportfahrplan, e.g.
#                        https://asvz.ch/426-sportfahrplan?f[0]=sport:45743 for
#                        volleyball. Make sure there starts only one lesson for
#                        that particular time at that particular location (i.e.
#                        use ASVZ filters).
