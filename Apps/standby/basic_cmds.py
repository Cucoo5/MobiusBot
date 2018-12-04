import discord
import ast
import os
import glob
import pickle as pk
from time import localtime, strftime
import sys, traceback
import asyncio
import sys, traceback
from datetime import datetime, timedelta, date, time
from os.path import getmtime
import random as rand
import aiohttp
import urllib3
import certifi


from Bot import functions as fn

class stdbycmds(object):
    '''
    always active command system
    scrubs through messages and prepares them for input into other modules.
    *may rename to servercmds
    '''
    def __init__(self,client,commandprefix,vnum):
        self.commandprefix=commandprefix #bot command prefix
        self.vnum=vnum #version number reference
        self.client=client #used here only to make sure the client object is available

        #get cmdlist
        self.cmdlst=[]
        self.mstcmds=[]
        docfile=open("./Info/cmdlst.txt","r")
        for line in docfile:
            line=line.split('-')
            command=line[0].strip()
            if command == "MASTER":
                cmd=line[1].strip()
                self.mstcmds.append(cmd)
            else:
                self.cmdlst.append(command)
        docfile.close()

        print("Master Command List:",self.mstcmds)

        self.badcnt={}

    def in_and_out(self,message):
        '''
        Takes message, processes and logs it,
        and packs the output if a command is found
        otherwise logs message only

        Central command function
        '''
        #get message
        self.message=message
        self.ch=self.message.channel
        self.usr=self.message.author

        self.master=fn.getmasterobj()
        output=None

        if self.usr not in self.badcnt:
            self.badcnt[self.usr]=0

        # get cmdin and context
        cmdin,cmdcntxt=fn.getcommandline(message,self.commandprefix)

        #looks for command and runs matching function.
        if cmdin != None:
            commandinput=cmdin.strip(self.commandprefix).lower()
            if commandinput.lower() == "mobius":
                commandinput=cmdcntxt.split()[0]
                cmdcntxt=cmdcntxt.replace(commandinput+" ", "")

            if commandinput in self.cmdlst:
                '''
                Add command functions here.
                Make sure command check matches word in command list
                '''

                if commandinput == "help":
                    msg=self.__bothelp()
                    output=fn.outputconstructor(self.client,"embed",self.ch,msg)
                    eventinfo="executed: "+commandinput

                if commandinput=="info":
                    msg=self.__info()
                    output=fn.outputconstructor(self.client,"embed",self.ch,msg)
                    eventinfo="executed: "+commandinput

                if commandinput=="versionlog":
                    msg=self.__versionlog()
                    output=fn.outputconstructor(self.client,"embed",self.ch,msg)
                    eventinfo="executed: "+commandinput

                if commandinput=="badcmd":
                    msg=self.__badcmd()
                    output=fn.outputconstructor(self.client,"string",self.ch,msg)
                    eventinfo="executed: "+commandinput

                if commandinput=="echo":
                    msg=self.__echo(cmdcntxt)
                    output=fn.outputconstructor(self.client,"string",self.ch,msg)
                    eventinfo="executed: "+commandinput

                if commandinput=="time":
                    msg=self.__timecmd()
                    output=fn.outputconstructor(self.client,"string",self.ch,msg)
                    eventinfo="executed: "+commandinput

                if commandinput=="rng":
                    msg=self.__randintcmd(cmdcntxt)
                    output=fn.outputconstructor(self.client,"string",self.ch,msg)
                    eventinfo="executed: "+commandinput

                if commandinput=="register":
                    msg,cmd=self.__registercmd()
                    output=fn.outputconstructor(self.client,"string",self.ch,msg,command=cmd)
                    eventinfo="executed: "+commandinput

                if commandinput=="save":
                    msg=self.__msgattachments()
                    output=fn.outputconstructor(self.client,"string",self.ch,msg)
                    eventinfo="executed: "+commandinput

                if commandinput=="retrieve":
                    msg,type,status=self.__getfilecmd(cmdcntxt)
                    output=fn.outputconstructor(self.client,type,self.ch,msg)
                    eventinfo="executed: "+commandinput
                    if status == 1:
                        raise ValueError("Multiple Files Found in retrieval.")

                if commandinput=="filelist":
                    msg=self.__getfolderfilelist()
                    output=fn.outputconstructor(self.client,"embed",self.ch,msg)
                    eventinfo="executed: "+commandinput


            if commandinput in self.mstcmds:
                if self.usr==self.master:
                    # add master commands here
                    if commandinput == "shutdown":
                        print("Logoff Command Received")
                        msg = "Mobius System Shutting Down."
                        cmd = ["logoff"]
                        output=fn.outputconstructor(self.client,"string",self.ch,msg,command=cmd)
                        eventinfo="executed: "+commandinput

                    if commandinput == "restart":
                        print("Reload Command Received")
                        msg = "Mobius System Restarting."
                        cmd = ["reload"]
                        output=fn.outputconstructor(self.client,"string",self.ch,msg,command=cmd)
                        eventinfo="executed: "+commandinput

                else:
                    msg="Access Denied."
                    self.badcnt[self.usr]+=1
                    eventinfo="Access Restricted to following: "+commandinput
                    if self.badcnt[self.usr]==5:
                        msg+="https://i.imgur.com/LtZ9oxF.png?1"
                        self.badcnt[self.usr]=0

                    output=fn.outputconstructor(self.client,"string",self.ch,msg)

            if commandinput not in self.cmdlst and commandinput not in self.mstcmds:
                msg="Command '"+commandinput+"' not available"+"\n"

                self.badcnt[self.usr]+=1
                eventinfo="Bad Command entered: "+commandinput + " | Count:" +str(self.badcnt[self.usr])

                if self.badcnt[self.usr]==5:
                    msg+="https://i.imgur.com/LtZ9oxF.png?1"
                if self.badcnt[self.usr] == 10:
                    msg+="https://www.youtube.com/watch?v=S4bmCvekW48"
                if self.badcnt[self.usr] == 15:
                    msg+="https://www.youtube.com/watch?v=l60MnDJklnM"
                    #reset bad command counter
                    self.badcnt[self.usr]=0

                output=fn.outputconstructor(self.client,"string",self.ch,msg)

            fn.eventlogger(self.message,eventinfo)

        return output

    def __bothelp(self):
        '''
        Get command list and documentation
        '''
        embed = discord.Embed(title="Mobius Help", description="Documentation of all standby commands", color=0xeee657)
        docfile=open("./Info/cmdlst.txt","r")
        for line in docfile:
            line=line.split('-')
            command=line[0].strip()
            if command != "MASTER":
                doc=line[1].strip()
                embed.add_field(name=command, value=doc)
            else:
                continue

        docfile.close()

        return embed

    def __info(self):
        embed = discord.Embed(title="Mobius", description="Running MobiOS "+self.vnum, color=0xeee657)
        embed.add_field(name="Author", value="Cicero")
        docfile=open("./Info/changelog.txt","r")

        for line in docfile:
            line=line.split(':')
            vnum1=line[0].strip()
            info1=line[1].strip()
            if vnum1 == self.vnum:
                infodoc=info1

        embed.add_field(name="Version Info", value=infodoc)
        return embed

    def __versionlog(self):
        embed = discord.Embed(title="Mobius Version Log", description="Version History", color=0xeee657)
        docfile=open("./Info/changelog.txt","r")
        for line in docfile:
            line=line.split(':')
            vnum1=line[0].strip()
            info1=line[1].strip()
            embed.add_field(name=vnum1, value=info1)
        return embed

    def __badcmd(self):
        raise ValueError("Error testing")
        return "Error testing"


    def __echo(self,words):
        '''
        returns a copy of the message after the command, italicized.
        '''
        if words != None and len(words) != 0:
            msg="*"
            msg+=words
            msg+="*"

        else:
            msg="*The soft chirping of crickets can be heard*"

        return msg

    def __timecmd(self):
        '''
        Gets current server time
        '''
        time=strftime("%Y-%m-%d %H:%M:%S", localtime())
        msg="Current time is: "+time+" EST"
        return msg

    def __randintcmd(self,minmax):
        '''
        generates a random integer number from 0-100
        '''
        if minmax==None:
            min=0
            max=100
        else:
            mm=minmax.split(",")
            min=int(mm[0].strip())
            max=int(mm[1].strip())
        number=str(rand.randint(min,max))

        return number

    def __registercmd(self):
        '''
        manual register command
        '''
        msg="Performing Registration Check"
        cmd = ["register"]
        return msg,cmd

    def __getfilecmd(self,words):
        '''
        retrieve a saved file in folder
        '''
        usr=self.usr
        usrinfo=fn.packuserinfo(usr)
        filename=words.strip()
        fldr=usrinfo["folder"]

        status=0

        f=glob.glob(fldr+"/**/"+filename,recursive=True)
        if len(f)==1:
            msg=f[0].replace("\\","/")
            type="file"

        elif len(f)==0:
            msg="Error: File not found."
            type="string"

        elif len(f)>1:
            msg="Error: Multiple files found."
            type="string"
            status=1

        return msg,type,status

    def __getfolderfilelist(self):
        '''
        retrieve all folders and files available to user
        '''
        usr=self.usr

        embed = discord.Embed(title="User", description="File List", color=0xeee657)

        folderdict=fn.getusrfolderfilelist(usr)

        n=0
        for key,value in folderdict.items():
            if len(value) != 0:
                n+=1
                embed.add_field(name="Folder: "+key,value=str(value))

        if n==0:
            embed.add_field(name="No Files",value="Found.")

        return embed


    def __msgattachments(self):
        '''
        checks message for attachments and stores it
        '''
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
        attch= self.message.attachments

        usrinfo=fn.packuserinfo(self.usr)
        usrdlfolder=usrinfo["folder"]+"/downloads"
        if not os.path.exists(usrdlfolder):
            os.makedirs(usrdlfolder)
            fn.desktopiniclr()

        # go through message attachments and download to user file
        if len(attch) != 0:
            for line in attch:
                fileurl=line["url"]
                filename=line["filename"]
                filechecklist=glob.glob(usrinfo["folder"]+"/*/**/"+filename,recursive=True)
                if len(filechecklist)!=0:
                    msg="Cannot save file. File already exists in another directory.\n"
                    for line in filechecklist:
                        l=line.replace("\\","/").replace(usrinfo["folder"],"")
                        msg+=l+"\n"

                else:
                    msg="Attachment saved."

                r = http.request('GET',fileurl,preload_content=False)
                with open(usrdlfolder+"/"+filename, 'wb') as out:
                    while True:
                        data = r.read(2**16)
                        if not data:
                            break
                        out.write(data)

                r.release_conn()
        else:
            msg="No files found. Please attach files to save."

        return msg

    def __movefilecmd(self,context):
        '''
        moves file to selected folder
        '''

        folderfilelist=context.split(",").strip()
        filecheck= folderfilelist[0]
        foldercheck= folderfilelist[1]

        folderdict=fn.getusrfolderfilelist(usr)

        usrinfo=packuserinfo(usr)
        fldr=usrinfo["folder"]

        folderfound=False
        filefound=False

        originfolder=""

        for key,value in folderdict.items():
            if key == foldercheck:
                folderfound=True

            if filecheck in value:
                filefound=True
                originfolder=key

            if key == foldercheck and filecheck in value:
                msg="File already in folder."
                break


        if folderfound and filefound:
            os.rename(fldr+originfolder+filecheck,fldr+foldercheck+filecheck)

        elif folderfound==False and filefound==False:
            
