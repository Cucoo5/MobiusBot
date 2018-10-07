import discord
import os
from time import gmtime, strftime
import sys, traceback

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
        self.badcnt={}
        self.master=fn.getmasterobj()


        if self.usr not in self.badcnt:
            self.badcnt[self.usr]=0

        # get cmdin and context
        cmdlist=fn.getcommandline(message,self.commandprefix)

        #looks for command and runs matching function.
        #outputlist=[]  seems to be for multi commands. get rid of later.

        for cmdin in cmdlist:
            if cmdin != None:
                commandinput=cmdin[0].strip(self.commandprefix)
                cmdcntxt=cmdin[1]
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

                    else:
                        output=fn.outputconstructor(self.client,"module",self.ch,cmdin)
                        eventinfo="packed info for module use."

                if commandinput in self.mstcmds:
                    if self.usr==self.master:
                        # add master commands here
                        if commandinput == "shutdown":
                            print("Logoff Command Received")
                            msg = "Mobius System Shutting Down."
                            cmd = ["logoff"]
                            output=fn.outputconstructor(self.client,"string",self.ch,msg,command=cmd)
                            eventinfo="executed: "+commandinput

                        else:
                            msg="Access Denied."
                            self.badcnt[self.usr]+=1

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

            else:
                output=None

            #outputlist.append(output)

        #return outputlist
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
        if len(words) != 0:
            msg="*"
            msg+=words
            msg+="*"

        else:
            msg="*The soft chirping of crickets can be heard*"

        return msg

    def __timecmd(self):
        '''
        Gets current time in GMT
        '''
        time=str(self.message.timestamp)
        msg="Current time is: "+time+" GMT"
        return msg
