import smtplib
import configparser
import csv
import copy
import random
from email.mime.text import MIMEText

cronies = []
allMatches = []
delMatches = []
ianMatches = []

#  Snag the email props
emailConfig = configparser.RawConfigParser()
emailConfigFilePath = r'email.settings'
emailConfig.read(emailConfigFilePath)

#  Fetch the data from the CSV and place it into an array that we'll use to generate matches
with open('secret_santa_responses.csv', newline='') as secretSantaFile:
    secretSantaResponses = csv.DictReader(secretSantaFile, delimiter=',')
    for crony in secretSantaResponses:
        cronies.append({'Name' : crony['Who are you?'], 
                        'Address' : crony['What address should your present be delivered to?'], 
                        'Naughty or Nice' : crony['Have you been naughty or nice this year?'], 
                        'Jokes' : crony['How do you feel about presents which are inside jokes?'],
                        'Hobbies' : crony['What hobbies or interests do you have that could guide your Simp to getting the perfect gift?'],
                        'Additional Info' : crony['Any additional info?'],
                        'Email' : crony['What is your email (this is how you will be notified of your recipient!']})

#  Deep copy cronies so we can remove matched simps
clonies = copy.deepcopy(cronies)

#  Generate a match dictionary 
for crony in cronies:
    matchNotFound = True

    #  My poor recreation of a do-while loop in Python, you'll never take the C out of this boy
    while matchNotFound:
        match = clonies[random.randrange(len(clonies)) if len(clonies) > 1 else 0]

        if (match['Name'] != crony['Name']):
            matchText = crony['Name'] + ' matched with ' + match['Name']
            print(matchText)

            if (crony['Name'] != 'FLY'):
                delMatches.append(matchText)
            elif (crony['Name'] != 'Ian'):
                ianMatches.append(matchText)

            allMatches.append(matchText)

            msg = MIMEText('Surprise 😳')

            msg['Subject'] = 'Hola Croñy, get excited because Simp-mas is finally here! 🎄'
            msg['From'] = emailConfig.get('smtp', 'sender')
            msg['To'] = crony['Email']

            #  For some reason I have to literally hard code the server here or it doesn't work. This is why Python is not webscale or production ready like Rust.
            with smtplib.SMTP('localhost', int(emailConfig.get('smtp', 'port'))) as smtp:
                if (emailConfig.get('smtp', 'isdev') == 'False'):
                    smtp.login(emailConfig.get('smtp', 'username'), emailConfig.get('smtp', 'password'))
                smtp.send_message(msg)
            
            #  Remove the match from clonies and break the loop
            clonies.remove(match)
            matchNotFound = False

print('All matches made, sending match-list to Delaney/Ian and generating hard copy master list')

#  Send all matches san Delany's to her
msg = MIMEText('\n'.join(delMatches))

msg['Subject'] = '2020 Cronies Secret Simp Match List'
msg['From'] = emailConfig.get('smtp', 'sender')
msg['To'] = emailConfig.get('smtp', 'delMail')

with smtplib.SMTP('localhost', int(emailConfig.get('smtp', 'port'))) as smtp:
    if (emailConfig.get('smtp', 'isdev') == 'False'):
        smtp.login(emailConfig.get('smtp', 'username'), emailConfig.get('smtp', 'password'))
    smtp.send_message(msg)

#  Do the same for myself
msg = MIMEText('\n'.join(ianMatches))

msg['Subject'] = '2020 Cronies Secret Simp Match List'
msg['From'] = emailConfig.get('smtp', 'sender')
msg['To'] = emailConfig.get('smtp', 'ianMail')

with smtplib.SMTP('localhost', int(emailConfig.get('smtp', 'port'))) as smtp:
    if (emailConfig.get('smtp', 'isdev') == 'False'):
        smtp.login(emailConfig.get('smtp', 'username'), emailConfig.get('smtp', 'password'))
    smtp.send_message(msg)

#  Finally generate a backup file containing all matches
backup = open('2020_secret_simp_matches.txt', 'w+')
backup.write('\n'.join(allMatches))