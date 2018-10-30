import discord
import ast
import os
import glob
import pickle as pk
from time import localtime, strftime
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
Can store information into a google drive for logs and save states.
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
usractivelst=None
stdby_app=None

#-------------------------------------------------------------------------------

# get master object
master=fn.getmasterobj()

# registered user object list
userlist=open("./Mobius_logs/Logs_User/userlist.txt","r")
usrlst={}
for line in userlist:
    userinfo=line.strip()
    usr=fn.userdict(userinfo)
    usrlst[userinfo]=usr

userlist.close()

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
        - mainly for commands and logoff

    * could be expanded later
    '''
    global activeclient

    outsys,command=fn.unpackoutput(output)

    if outsys != None:
        for i in range(len(outsys)):
            cmd=command[i]
            if cmd != None:
                #if cmd[0] == "activate":
                #    usr=cmd[1]
                #    appname=cmd[2]
                #    appactivator(usr,appname)
                if cmd[0] == "logoff":
                    outsys.append(client.logout())

    return outsys

#def appactivator(usr,appname,client):
#    '''
#    gets the app for the user.
#    '''
#    usrnm=str(usr)
#    if appname == "standby":
#        app=stdby_app
#
#    if appname == "proto":
#        #app=mobius.proto
#        pass
#
#    global usractivelst
#    usractivelst[usrnm]=[appname,app,usr]

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

        svroutput = stdby_app.in_and_out(message)


        if userinfo in usractivelst:
            output = svroutput
        # remove initialize system.
        #    usrstatus=usractivelst[userinfo][0]
        #    usrapp=usractivelst[userinfo][1]
        #    if usrstatus != "initialize":
        #        if message.content.startswith(commandprefix+"mobius") or usrstatus == "standby":
        #            output=svroutput
        #        else:
        #            output = usrapp.in_and_out(message)

        else:
            usractivelst[userinfo]=["standby",stdby_app,usrobj]
            msg="Welcome, "+usrnm+"."+"\n"
            msg+="For convenience, your user information has been saved to the Mobius database."+"\n"
            msg2=fn.register(usrobj)
            eventinfo = "user registered: "+usrobj.name
            fn.eventlogger(message,eventinfo)
            output = svroutput
            await client.send_message(usrobj, msg)
            await client.send_message(master, msg2)

        if output != None:
            for output in outputhandler(output):
                await output

                ####Cannot do the below. could maybe use on rpassist.
                # save server object on successful command
                #datetime=fn.get_time()
                #tlist=datetime.split()
                #date=tlist[0]
                #time=tlist[1]
                #tstring=date+"_"+time
                #
                #with open("./Mobius_Server/serversaves/svrsv_"+tstring+".pkl","wb") as save:
                #    pk.dump(stdby_app,save)
                #save.close()

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

    # context menu system
    global usractivelst
    usractivelst={}

    # apps initialize (Add new apps here)
    global stdby_app
    #list_of_saves = glob.glob('./Mobius_Server/serversaves/*.pkl')
    #if len(list_of_saves) == 0: #this is the initialization check

    stdby_app=cmdmng.stdbycmds(activeclient,commandprefix,vnum)

    #else:
    #    latest_save = str(max(list_of_saves, key=os.path.getctime)).replace('\\','/')
    #    print(latest_save)
    #    with open(latest_save,"rb") as load:
    #        stdby_app = pk.load(load)

    global rp_assistant
    #list_of_saves = glob.glob('./Mobius_Server/rpassistantsaves/*.pkl')
    #if len(list_of_saves) == 0: #this is the initialization check

    rp_assistant=rpa.rpassistant(activeclient,commandprefix,vnum)

    #else:
    #    latest_save = str(max(list_of_saves, key=os.path.getctime)).replace('\\','/')
    #    with open(latest_save,"rb") as load:
    #        rp_assistant = pk.load(load)


    # user list
    global usrlst
    if usrlst != {}:
        for user in list(usrlst.keys()):
            if user not in usractivelst:
                usrobj=usrlst[user]
                usractivelst[user]=["standby",stdby_app,usrobj]

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
async def my_background_task():

    await client.wait_until_ready()
    counter = 0
    channel = discord.Object(id='443052380800417802')
    while not client.is_closed:
        await client.send_message(channel, 'Hours without something going horribly wrong: '+ str(counter))
        counter += 1
        await asyncio.sleep(3600) # task runs every 3600 seconds (1 hr)

async def server_tick():
    '''
    syncs bot time with midnight EST and then
    executes functions at midnight EST
    '''
    await client.wait_until_ready()
    channel = discord.Object(id='506628142455324692') # mobius_news channel

    while not client.is_closed:
        # find wait time to midnight
        datetime = fn.get_time()
        time=datetime.split()[1]
        tlist=time.split('-')
        hour=int(tlist[0])
        minute=int(tlist[1])
        second=int(tlist[2])
        hours=24-hour
        minutes=0-minute
        seconds=0-second
        waittime=hours*3600+minutes*60+seconds

        await client.send_message(channel, 'Mobius Server Update')
        await asyncio.sleep(waittime) # task waits until midnight

client.loop.create_task(my_background_task())

client.run(TOKEN)
