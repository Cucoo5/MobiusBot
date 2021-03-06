import discord
import ast
import os
import glob
import pickle as pk
from time import localtime, strftime
import sys, traceback
import asyncio
from datetime import datetime, timedelta, date, time
from os.path import getmtime
import random as rand
import aiohttp
import urllib3
import certifi
import pandas as pd

from Bot import functions as fn

#import apps here
from Apps.standby import basic_cmds as cmdmng
from Apps.assistant import rpassist as rpa


'''
Dev Version

Script for a Discord bot
Powers a discord bot that can take inputs and post outputs.
Can store information as logs and files.
Automatically restarts when the code is updated.
'''

print("Initializing...")

devstate=True

TOKEN,commandprefix,serverid = fn.devinfo(devstate)

# client and server objects
client = discord.Client()
activeclient=client
server = discord.Server(id=serverid)

#get most recent version number
docfile=open("./Info/changelog.txt","r")
vnumlist=[]
for line in docfile:
    line=line.split(':')
    vnumlist.append(line[0].strip())

vnum=vnumlist[-1]
docfile.close()

errlog=None
stdby_app=None

#-------------------------------------------------------------------------------

# get master object
master=fn.getmasterobj()


# registered user object list
usrlst={}

#get user objects
list_of_users = glob.glob('./Mobius_Users/*/*.pkl')
for file in list_of_users:
    f=file.replace('\\','/')
    with open(f,"rb") as load:
        usr = pk.load(load)
    usrid=usr.id
    usrlst[usr.id]={"usrobj":usr}


#-------------------------------------------------------------------------------

# bot output handler
def outputhandler(output,usr):
    '''
    Takes output and performs appropriate action

    string type:
        - can send string messages to different destinations
    embed type:
        - can send embed messages to different destinations

    command:
        - sends messages of out type and executes command for the bot
        - mainly for master commands

    * could be expanded later
    '''
    global activeclient
    global master
    global usrlst

    usrid=usr.id

    outsys,command=fn.unpackoutput(output)

    if outsys != None:
        for i in range(len(outsys)):
            cmd=command[i]
            if cmd != None:
                if cmd[0] == "logoff":
                    outsys.append(client.logout())

                if cmd[0] == "reload":
                    outsys.append(os.execv(sys.executable, ['python']+sys.argv))

                if cmd[0] == "register":
                    msg2,status=fn.register(usr)
                    if userid in usrlst and status == False:
                        msg="Greetings, "+str(usr.name)+"."+"\n"
                        msg+="You are already registered within the Mobius database."+"\n"
                        outsys.append(client.send_message(usr, msg))
                    elif userid in usrlst and status == True:
                        msg="Greetings, "+str(usr.name)+"."+"\n"
                        msg+="Your user information has been reset."+"\n"
                        outsys.append(client.send_message(usr, msg))



    return outsys

#-------------------------------------------------------------------------------
# Additional bot functions

def is_me(msg):
    return msg.author==client.user

async def purgeannouncements(channel):
    async for msg in client.logs_from(channel):
        if msg.author==client.user or msg.content == ">>purge":
            await client.delete_message(msg)

    await client.send_message(master, "announcements purged")


async def create_role(usr,rolename,color):
    '''
    Creates a role, and adds user to that role.

    '''

    channel=discord.Object(id="443052380800417802")

    global client
    global server

    svr=server

    #try:
    await client.create_role(server=svr,name=rolename)
    rolelist=svr.roles
    print(len(rolelist)) #=0
    #roleobj=discord.Role(server=svr,name=rolename)
    #memberobj=svr.get_member(usr.id)
    #await client.add_roles(memberobj,roleobj)
        #msg="Role Created."
    #msg="test"

    #except:
        #msg="Role Creation and Join Failed. Role may already exist or User cannot Join Role."


    await client.send_message(channel,msg)

#-------------------------------------------------------------------------------
# bot event functions
@client.event
async def on_message(message):

    usr=message.author
    usrid=usr.id
    userdict=fn.packuserinfov2(usr)

    ch=message.channel

    # Prevent bot from replying to self, unless is file message
    if usr == client.user:
        botID=client.user.id
        if message.content.startswith(">!>FileToSave:"+botID):

            eventinfo="Saving self-created file"
            fn.eventlogger(message,eventinfo)
            await client.delete_message(message)


    try:
        global commandprefix
        if message.content.startswith(commandprefix):

            output = stdby_app.in_and_out(message)

            if output != None:
                for output in outputhandler(output,usr):
                    await output


            if usrid not in usrlst:
                fn.desktopiniclr()
                msg="Welcome, "+str(usr.name)+"."+"\n"
                msg+="For convenience, your user information has been saved to the Mobius database."+"\n"
                msg2,status=fn.register(usr)
                eventinfo = "user registered: "+usrobj.name
                fn.eventlogger(message,eventinfo)
                await client.send_message(usr, msg)
                await client.send_message(master, msg2)

                usrlst[usrid]={"usrobj":usr}

        elif message.content.startswith(">>purge") and usr == master:
            channel=discord.Object(id="443783466400612354")
            await purgeannouncements(channel)

        elif message.content.startswith(">>create_role") and usr == master:
            options=str(message.content).replace(">>create_role","").strip().split(',')

            try:
                usrid=options[0]
                usr=discord.Object(id=usrid)
                rolename=options[1]
                color=options[2]

            except:
                msg="Error: Invalid Input."

            await create_role(usr,rolename,color)


    except:
        errlog.logerror(message)
        output=errlog.errormsg()
        for output in outputhandler(output,usr):
            await output

def status_send():
    msg='Mobius Startup complete'
    ch=discord.Object(id='443052380800417802')
    global activeclient
    outstatus=activeclient.send_message(ch, msg)
    return outstatus


# on initalize
@client.event
async def on_ready():
    print("Initialization Complete.")
    global activeclient
    activeclient=client

    # error logger
    global errlog
    errlog=fn.errorlogger(activeclient)

    # apps initialize (Add new apps here)
    global stdby_app
    stdby_app=cmdmng.stdbycmds(activeclient,commandprefix,vnum)

    #    latest_save = str(max(list_of_saves, key=os.path.getctime)).replace('\\','/')
    #    print(latest_save)
    #    with open(latest_save,"rb") as load:
    #        stdby_app = pk.load(load)

    #global rp_assistant
    #rp_assistant=rpa.rpassistant(activeclient,commandprefix,vnum)

    # sanity check
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print("Running Version: ",vnum)
    print('--------------------------')
    await status_send()

#-------------------------------------------------------------------------------

# timer based functions

async def update_warning():

    await client.wait_until_ready()
    counter = 0
    channel = discord.Object(id='443783466400612354')
    Watched_files=[__file__,'./Bot/functions.py','./Apps/standby/basic_cmds.py']
    Watched_files_MTimes = [(f,getmtime(f)) for f in Watched_files]

    state=0

    mentionprefix =''

    warningtimes={"minutes":(1,5,10,30),"hours":(1,5,10)}
    warningtimedeltas=[]
    for key,value in warningtimes.items():
        if key == "minutes":
            for minute in value:
                timed=timedelta(minutes=minute)
                warningtimedeltas.append(timed)
        elif key == "hours":
            for hour in value:
                timed=timedelta(hours=hour)
                warningtimedeltas.append(timed)

    warningtimedeltas.sort(reverse=True)

    global devstate

    while not client.is_closed:

        # find wait time to next warning
        currenttime = datetime.today()
        midnight=datetime.combine(date.today()+timedelta(days=1),time(hour=0))
        timetomidnight=midnight-currenttime
        midnightwaittime=timetomidnight.seconds

        minutewaittime=60-currenttime.second

        #create time to midnight string
        timestr=str(timetomidnight)

        #check for updates and creates warning.
        for f, mtime in Watched_files_MTimes:
            if getmtime(f) != mtime:
                print("Update Ready.")
                state=1

        if state != 0:
            for timed in warningtimedeltas:
                if timetomidnight>=timed:
                    timeto=timetomidnight-timed
                    timetowait=timeto.seconds
                    if timed == warningtimedeltas[-1]:
                        state=3
                    break


            if state == 1 and devstate != True:
                mentionprefix='@everyone: '
                state=2
            elif state == 2:
                mentionprefix=''
            elif state == 3:
                mentionprefix='@here: '

            await client.send_message(channel, mentionprefix+'Mobius System Update Found. Updating in '+timestr.split(".")[0])

        else:
            timetowait = minutewaittime

        await asyncio.sleep(timetowait) # task runs by default every minute, unless an update is found.


async def server_tick():
    '''
    syncs bot time with midnight EST and then
    executes functions at midnight EST
    - Restarts Mobius if code changes
    - Clears Message logs to certain date
    '''
    await client.wait_until_ready()
    channel1 = discord.Object(id='443783466400612354') # announcement channel
    channel2 = discord.Object(id='443052380800417802') # bot testing channel

    counter=0
    print("server_tick")

    Watched_files=[__file__,'./Bot/functions.py','./Apps/standby/basic_cmds.py']
    Watched_files_MTimes = [(f,getmtime(f)) for f in Watched_files]

    while not client.is_closed:

        fn.msglogclearer()
        fn.desktopiniclr()

        #check for updates and restart
        for f, mtime in Watched_files_MTimes:
            if getmtime(f) != mtime:
                print("Preparing Update. Restarting. \n--------------------------")
                await client.send_message(channel1, 'Restarting...')
                os.execv(sys.executable, ['python']+sys.argv)

        # find wait time to midnight
        currenttime = datetime.today()
        midnight=datetime.combine(date.today()+timedelta(days=1),time(hour=0))
        timetomidnight=midnight-currenttime
        waittime=timetomidnight.seconds

        print("waittime: ",waittime)
        print("time: ",currenttime)

        await client.send_message(channel2, 'Mobius Server system check: '+str(counter))
        counter+=1
        await asyncio.sleep(waittime) # task waits until midnight

client.loop.create_task(update_warning())
client.loop.create_task(server_tick())

client.run(TOKEN)
