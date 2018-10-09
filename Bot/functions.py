import discord
import os
from time import localtime, strftime
import sys, traceback
import pickle as pk

def devinfo(devstate):
    # token management
    devetoken = 'NDQzMDQ3MTIyNjE1NjY0NjU1.DdHrvQ.jzHf-bcBK6irM-EdJ89jXOj7wfk'
    livetoken = 'NDQzMDU4OTM1Nzg0NjY5MTk0.DdH2Ug.vJx_2Xw-GHdqvlks7OB7N2WYTh0'

    if devstate:
        usetoken=devetoken
        commandprefix='<<'
    else:
        usetoken=livetoken
        commandprefix='>>'

    return usetoken,commandprefix

def getcommandline(message,commandprefix):
    '''
    gets line of message that contains potential commands

    currently designed to look for multi commands in any message, which doesn't
    work.
    '''
    characterlist=message.content
    state=0
    commandcharindex=0
    endcharindex=0

    linelist=characterlist.splitlines()

    commandlist=[]

    for line in linelist:
        line=line.split()
        if commandprefix in line[0]:
            commandinput = line[0]
            commandcontext = line.remove(commandinput)
            wordstring=None
            if commandcontext != None:
                if len(commandcontext) >=1:
                    i=0
                    wordstring=""
                    for word in commandcontext:
                        if i == 0:
                            wordstring+=word
                            i+=1
                        else:
                            wordstring+=" "+word

            commandlist.append((commandinput,wordstring))

        else:
            continue


    return commandlist

def get_time():
    '''
    returns local time as string.
    '''
    time=strftime("%Y-%m-%d %H-%M-%S", localtime())
    return time

def eventlogger(msg,eventinfo,type="event"):
    time=get_time()
    tlist=time.split()
    date=tlist[0]

    if type == "event":
        logfile=open("./Mobius_logs/Logs_Event/eventlog_"+date+".txt","a+")

    elif type == "error":
        logfile=open("./Mobius_logs/Logs_Error/errorlog_"+date+".txt","a+")

    author=str(msg.author.name)
    channel=str(msg.channel)
    message=str(msg.content)
    logmsg=time+" - "+author+" sent to channel "+channel+" : "+message+" | "+eventinfo+"\n"
    logfile.write(logmsg)
    logfile.close()

    with open("./Mobius_logs/Logs_Messages/"+time+"_"+channel+"_"+author+".pkl","wb") as save:
        pk.dump(msg,save)
    save.close()


class errorlogger(object):
    '''
    Sets up error logging for any module
        - Place at init of module.
    '''
    def __init__(self,client):
        self.errcnt={}
        self.client=client

    def logerror(self,message):
        usr=message.author
        self.message=message

        if usr.name not in self.errcnt:
            self.errcnt[usr.name]=1
        else:
            self.errcnt[usr.name]+=1

        if self.errcnt[usr.name] >= 2:
            self.notistate=False
        else:
            self.notistate=True

        exc_type, exc_value, exc_traceback = sys.exc_info()

        self.errorinfo=traceback.format_exception(exc_type, exc_value, exc_traceback)

        self.errortrcbk=""
        for line in self.errorinfo:
            self.errortrcbk+=line


        eventlogger(self.message,self.errortrcbk,"error")

    def errormsg(self):

        msg="Error Caught On Command"+"\n"
        master=getmasterobj()
        output=outputconstructor(self.client,"string",self.message.channel,msg)
        if self.notistate:

            msg+="Event has been logged and a notification has been sent."
            output=outputconstructor(self.client,"string",self.message.channel,msg)

            msg2="An error has been found. Taceback is as follows:"+"\n"
            msg2+=self.errortrcbk
            output=outputconstructor(self.client,"string",master,msg2,output=output)

        return output

def register(usr):
    '''
    creates user folder with user object saved as pickle file.
    '''

    userinfo=packuserinfo(usr) #get string used in folder and object location

    #initalize and open userlist, which contains backup of info
    userlist=open("./Mobius_logs/Logs_User/userlist.txt","a+")

    if os.path.exists(userinfo["folder"]):
        msg="User has already been registered: "+str(usr)

    else:
        userlist.write(userinfo["string"]+"\n")

        # make user folder profile
        os.makedirs(userinfo["folder"]) # make user folder
        os.makedirs(userinfo["folder"]+"/user_rplist")
        os.makedirs(userinfo["folder"]+"/user_characters")
        os.makedirs(userinfo["folder"]+"/user_summaries")
        os.makedirs(userinfo["folder"]+"/user_todolists")
        os.makedirs(userinfo["folder"]+"/user_reminders")


        with open(userinfo["object"],"wb") as save:
            pk.dump(usr,save)
        save.close()

        msg="User has been registered: "+str(usr)

    userlist.close()

    return msg

def packuserinfo(usr):
    '''
    packs user name, discriminator, and id for folder and file access.
    '''
    username=str(usr.name)
    id=str(usr.id)
    discriminator=str(usr.discriminator)

    userinfo=username+discriminator+"_"+id
    usrdict=userdict(userinfo)
    return usrdict

def userdict(userinfo):
    '''
    gets the folder and file string
    '''
    userinfofolder="./Mobius_Users/"+userinfo
    infofile=userinfofolder+"/userinfo_"+userinfo+".pkl"
    usrdict={"string":userinfo,"folder":userinfofolder,"object":infofile}
    return usrdict


def getmasterobj():
    with open("./Info/masterinfo.pkl","rb") as load:
        master = pk.load(load)

    return master

def getusrobj(userdict):
    with open(userdict["object"],"rb") as load:
        user = pk.load(load)

    return user

def outputconstructor(client,outtype,ch,msg,command=None,output=None):
    '''
    helps construct output
    '''
    if outtype == "string":
        outsys = client.send_message(ch, msg)

    elif outtype == "embed":
        outsys = client.send_message(ch, embed=msg)

    elif outtype == "module":
        outsys = (ch,msg)

    if output == None:
        output=[(outsys,command)]
    else:
        output.append((outsys,command))
    return output

def unpackoutput(output):
    if output != None:
        outsys=[]
        command=[]
        for line in output:
            outsys.append(line[0])
            command.append(line[1])

        return outsys,command
    else:
        return None,None
