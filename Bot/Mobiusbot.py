import discord
import ast
import os
import glob
import pickle as pk
from time import localtime, strftime
from os.path import getmtime
import sys, traceback
import asyncio

from Bot import functions as fn

#import apps here
from Apps.standby import basic_cmds as cmdmng
from Apps.assistant import rpassist as rpa


'''
Dev Version

Script for a Discord bot
Powers a discord bot that can take inputs and post outputs.
Can store information into a for logs and save states.
Automatically restarts when the code is updated.
'''

print("Initializing...")

devstate=True

TOKEN,commandprefix = fn.devinfo(devstate)

# client and server objects
client = discord.Client()
activeclient=client
server = discord.Server(id='443051945016688640')

#get most recent version
docfile=open("./Info/changelog.txt","r")
vnumlist=[]
for line in docfile:
    line=line.split(':')
    vnumlist.append(line[0].strip())

vnum=vnumlist[-1]
docfile.close()

errlog=None
#usractivelst=None
stdby_app=None

#-------------------------------------------------------------------------------

# get master object
master=fn.getmasterobj()

# registered user object list
usrlst={}

#get user object files
list_of_users = glob.glob('./Mobius_Users/*/*.pkl')
for file in list_of_users:
    f=file.replace('\\','/')
    with open(f,"rb") as load:
        user = pk.load(load)
    usr=fn.packuserinfo(user)
    userinfo=usr['string']
    usrlst[userinfo]=usr

#-------------------------------------------------------------------------------

# bot output handler
def outputhandler(output):
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

    outsys,command=fn.unpackoutput(output)

    if outsys != None:
        for i in range(len(outsys)):
            cmd=command[i]
            if cmd != None:
                if cmd[0] == "logoff":
                    outsys.append(client.logout())

                if cmd[0] == "reload":
                    outsys.append(os.execv(sys.executable, ['python']+sys.argv))

    return outsys

#-------------------------------------------------------------------------------

# bot event functions
@client.event
async def on_message(message):

    usrobj=message.author
    usrnm=str(usrobj.name)
    userdict=fn.packuserinfo(usrobj)
    userinfo=userdict["string"]

    ch=message.channel

    # Prevent bot from replying to self
    if usrobj == client.user:
        return

    try:
        output = stdby_app.in_and_out(message)

        if userinfo not in usrlst:
            msg="Welcome, "+usrnm+"."+"\n"
            msg+="For convenience, your user information has been saved to the Mobius database."+"\n"
            msg2=fn.register(usrobj)
            eventinfo = "user registered: "+usrobj.name
            fn.eventlogger(message,eventinfo)
            await client.send_message(usrobj, msg)
            await client.send_message(master, msg2)

            usrlst[userinfo]=usrobj

        if output != None:
            for output in outputhandler(output):
                await output

    except:
        errlog.logerror(message)
        output=errlog.errormsg()
        for output in outputhandler(output):
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

    global rp_assistant
    rp_assistant=rpa.rpassistant(activeclient,commandprefix,vnum)

    # sanity check
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print("Running Version: ",vnum)
    print('--------------------------')
    await status_send()

#-------------------------------------------------------------------------------

# timer based functions

#example:
async def update_warning():

    await client.wait_until_ready()
    counter = 0
    channel = discord.Object(id='443783466400612354')
    Watched_files=[__file__,'./Bot/functions.py','./Apps/standby/basic_cmds.py']
    Watched_files_MTimes = [(f,getmtime(f)) for f in Watched_files]

    state=0

    mentionprefix =''

    global devstate

    while not client.is_closed:

        # find wait time to next warning
        datetime = fn.get_time()
        time=datetime.split()[1]
        tlist=time.split('-')

        #time components converted to seconds
        hour=int(tlist[0])*3600
        minute=int(tlist[1])*60
        second=int(tlist[2])
        timesum=hour+minute+second
        midnight=24*3600
        midnightwaittime=midnight-timesum
        minutewaittime=60-second
        hourwaittime=60-minute

        #create time to midnight string
        hoursto=midnightwaittime//3600
        minutesto=(midnightwaittime-(hoursto*3600))//60
        secondsto=((midnightwaittime-(hoursto*3600))-(minutesto*60))

        if hoursto < 10:
            hstr="0"+str(hoursto)
        else:
            hstr=str(hoursto)
        if minutesto < 10:
            mstr="0"+str(minutesto)
        else:
            mstr=str(minutesto)
        if secondsto < 10:
            sstr="0"+str(secondsto)
        else:
            sstr=str(secondsto)

        timetoupdatestr=hstr+":"+mstr+":"+sstr

        #check for updates and creates warning.
        for f, mtime in Watched_files_MTimes:
            if getmtime(f) != mtime:
                print("Update Ready.")
                state=1

        if state != 0:
            if (midnightwaittime-(10*3600)) >= 0:
                #set a 10 hr warning
                timetowait = (midnightwaittime-(10*3600))

            elif (midnightwaittime-(5*3600)) >= 0:
                #set 5 hr warning
                timetowait = (midnightwaittime-(5*3600))

            elif (midnightwaittime-(2*3600)) >= 0:
                #set 2 hr warning
                timetowait = (midnightwaittime-(2*3600))

            elif (midnightwaittime-(1*3600)) >= 0:
                #set 1 hr warning
                timetowait = (midnightwaittime-(1*3600))

            elif (midnightwaittime-(30*60)) >= 0:
                #set 30 min warning
                timetowait = (midnightwaittime-(30*60))

            elif (midnightwaittime-(15*60)) >= 0:
                #set 15 min warning
                timetowait = (midnightwaittime-(15*60))

            elif (midnightwaittime-(10*60)) >= 0:
                #set 10 min warning
                timetowait = (midnightwaittime-(10*60))

            elif (midnightwaittime-(5*60)) >= 0:
                #set 10 min warning
                timetowait = (midnightwaittime-(5*60))

            elif (midnightwaittime-(2*60)) >= 0:
                #set 2 min warning
                timetowait = (midnightwaittime-(2*60))
                state = 3

            elif (midnightwaittime-(1*60)) >= 0:
                #set 1 min warning
                timetowait = (midnightwaittime-(1*60))
                state = 3

            if state == 1 and devstate != True:
                mentionprefix='@everyone: '
                state=2
            elif state == 2:
                mentionprefix=''
            elif state == 3:
                mentionprefix='@here: '

            await client.send_message(channel, mentionprefix+'Mobius System Update Found. Updating in '+timetoupdatestr)

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

        #check for updates and restart
        for f, mtime in Watched_files_MTimes:
            if getmtime(f) != mtime:
                print("Update Found. Restarting. \n--------------------------")
                await client.send_message(channel1, 'Restarting...')
                await os.execv(sys.executable, ['python']+sys.argv)

        # find wait time to midnight
        datetime = fn.get_time()
        time=datetime.split()[1]
        tlist=time.split('-')

        #time components converted to seconds
        hour=int(tlist[0])*3600
        minute=int(tlist[1])*60
        second=int(tlist[2])
        timesum=hour+minute+second
        midnight=24*3600
        waittime=midnight-timesum

        print("waittime: ",waittime)
        print("time: ",time)

        await client.send_message(channel2, 'Mobius Server system check: '+str(counter))
        counter+=1
        await asyncio.sleep(waittime) # task waits until midnight

client.loop.create_task(update_warning())
client.loop.create_task(server_tick())

client.run(TOKEN)
