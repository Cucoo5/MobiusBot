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
import pandas as pd

import matplotlib.pyplot as plt

from html.parser import HTMLParser
from urllib import parse
from urllib.request import urlopen
from urllib.request import urlretrieve
import networkx as nx
import html2text


def devinfo(devstate):
    # token management + serverid
    tokenfile=open('./Info/token.txt')
    tokendict={}
    for line in tokenfile:
        temp=line.strip().split(" = ")
        tokenname=temp[0]
        tokenval=temp[1]
        tokendict[tokenname]=tokenval

    if devstate:
        usetoken=tokendict["devetoken"]
        commandprefix='<<'
    else:
        usetoken=tokendict["livetoken"]
        commandprefix='>>'

    serverid=tokendict["serverid"]

    return usetoken,commandprefix,serverid

def getcommandline(message,commandprefix):
    '''
    gets line of message that contains a potential command
    '''
    msg=message.content
    command=(None,None)
    if commandprefix in msg[0:2]: # look for commandprefix at start of message.
        context=msg.split()
        commandinput=msg.split()[0]
        context.remove(commandinput)

        # get context of command.
        wordstring=None
        if context != None:
            if len(context) >=1:
                i=0
                wordstring=""
                for word in context:
                    if i == 0:
                        wordstring+=word
                        i+=1
                    else:
                        wordstring+=" "+word

        command=(commandinput,wordstring)

    return command

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

def msglogclearer(num_days=187):
    '''
    Used to manage amount of log files.
    Keeps only those within input number of days.
    default: 187 days
    '''
    date = datetime.today() - timedelta(days=num_days)
    limittime=date.timestamp()
    list_of_logs = glob.glob('./Mobius_logs/Logs_Messages/*.pkl')
    logsMTimes = [(f,getmtime(f)) for f in list_of_logs]
    for f,t in logsMTimes:
        comparetime=float(t)
        if comparetime < limittime:
            os.remove(file)


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

    status=False

    if os.path.exists(userinfo["file"]):
        msg="User has already been registered: "+str(usr)

    else:
        if not os.path.exists(userinfo["folder"]):
            # make user folder profile
            # make user folder
            os.makedirs(userinfo["folder"])

        if not os.path.exists(userinfo["folder"]+"/downloads"):
            os.makedirs(userinfo["folder"]+"/downloads")

        if not os.path.exists(userinfo["folder"]+"/rpassistant"):
            #make rp assistant folder and subfolders
            os.makedirs(userinfo["folder"]+"/rpassistant")
            os.makedirs(userinfo["folder"]+"/rpassistant"+"/user_rplist")
            os.makedirs(userinfo["folder"]+"/rpassistant"+"/user_characters")
            os.makedirs(userinfo["folder"]+"/rpassistant"+"/user_summaries")
            os.makedirs(userinfo["folder"]+"/rpassistant"+"/user_todolists")
            os.makedirs(userinfo["folder"]+"/rpassistant"+"/user_reminders")

        #save user object
        with open(userinfo["file"],"wb") as save:
            pk.dump(usr,save)
        save.close()

        msg="User has been registered: "+str(usr)
        status=True

    return msg,status

def registerv2(usr):
    '''
    Creates user files to store information in CSV files using ID.
    '''
    status=False
    usrdict=packuserinfov2(usr)

    if os.path.exists(usrdict["usrfld"]):
        msg="User has already been registered: "+str(usr)

    else:
        if not os.path.exists(usrdict["usrfld"]):
            # make user folder profile
            # make user folder
            os.makedirs(usrdict["usrfld"])
            usrfoldercsv={"Folder":[],"FileName":[],"FileURL":[]}
            df=pd.DataFrame(data=usrfoldercsv)
            df.to_csv(usrdict["usrprof"],index=False)

            #save user object
            with open(usrdict["usrobjfile"],"wb") as save:
                pk.dump(usr,save)
            save.close()

        msg="User has been registered: "+str(usr)
        status=True

    return msg,status

def packuserinfo(usr):
    '''
    packs user name, discriminator, and id for folder and file access.
    '''
    username=str(usr.name)
    id=str(usr.id)
    discriminator=str(usr.discriminator)

    userinfo=username+discriminator+"_"+id
    usrdict=userdict(userinfo,usr)
    return usrdict

def packuserinfov2(usr):
    '''
    gets the folder and file string for usr
    '''
    usrID=str(usr.id)
    usrfld="./Mobius_Users/"+usrID #folder for user
    usrprof=usrfld+"/"+"userprofile_"+usrID+".csv"
    usrobjfile=usrfld+"/"+usrID+".pkl"

    usrdict={"usrID":usrID,"usrfld":usrfld,"usrprof":usrprof,"usrobjfile":usrobjfile,"usr":usr}

    return usrdict

def userdict(userinfo,usr):
    '''
    gets the folder and file string
    '''
    userinfofolder="./Mobius_Users/"+userinfo
    infofile=userinfofolder+"/userinfo_"+userinfo+".pkl"
    usrdict={"string":userinfo,"folder":userinfofolder,"file":infofile,"object":usr}

    return usrdict

def getmasterobj():
    with open("./Info/masterinfo.pkl","rb") as load:
        master = pk.load(load)

    return master

def getusrobj(userdict):
    with open(usrdict["usrobjfile"],"rb") as load:
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

    elif outtype == "file":
        outsys = client.send_file(ch, fp=msg)

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

def desktopiniclr():
    desktopinilist=[x.replace("\\","/") for x in glob.glob("./**/desktop.ini",recursive=True)]
    for line in desktopinilist:
        os.remove(line)


"""
class LinkParser(HTMLParser):

    # This is a function that HTMLParser normally has
    # but we are adding some functionality to it
    def handle_starttag(self, tag, attrs):
        # We are looking for the begining of a link. Links normally look
        # like <a href="www.someurl.com"></a>
        if tag == 'a':
            for (key, value) in attrs:
                if key == 'href':
                    # We are grabbing the new URL. We are also adding the
                    # base URL to it. For example:
                    # www.netinstructions.com is the base and
                    # somepage.html is the new URL (a relative URL)
                    #
                    # We combine a relative URL with the base URL to create
                    # an absolute URL like:
                    # www.netinstructions.com/somepage.html
                    newUrl = parse.urljoin(self.baseUrl, value)
                    # And add it to our colection of links:
                    self.links = self.links + [newUrl]

    # This is a new function that we are creating to get links
    # that our spider() function will call
    def getLinks(self, url,restriction=""):
        self.links = []
        # Remember the base URL which will be important when creating
        # absolute URLs
        self.baseUrl = url + restriction
        # Use the urlopen function from the standard Python 3 library
        response = urlopen(url)
        # Make sure that we are looking at HTML and not other things that
        # are floating around on the internet (such as
        # JavaScript files, CSS, or .PDFs for example)
        if 'text/html' in response.getheader('Content-Type'):
            htmlBytes = response.read()
            # Note that feed() handles Strings well, but not bytes
            # (A change from Python 2.x to Python 3.x)
            htmlString = htmlBytes.decode("utf-8")
            self.feed(htmlString)
            return htmlString,self.links #htmlString, self.links
        if 'text/plain' in response.getheader('Content-Type'):
            return url,[]
        else:
            return "",[]


def spider(url, maxPages):
    '''
    Main spider function to listen to a forum and get post statistics.
    '''

    pagesToVisit = [url]
    numberVisited = 0
    foundWord = False

    allpages=[url]

    G=nx.Graph()

    # The main loop. Create a LinkParser and get all the links on the page.
    # Also search the page for the word or string
    # In our getLinks function we return the web page
    # (this is useful for searching for the word)
    # and we return a set of links from that web page
    # (this is useful for where to go next)

    while numberVisited < maxPages and pagesToVisit != []:
        # Start from the beginning of our collection of pages to visit:
        url = pagesToVisit[0]

        pagesToVisit = pagesToVisit[1:]

        G.add_node(url)

        try:
            print(numberVisited, "Visiting:", url)
            parser = LinkParser()
            data, links = parser.getLinks(url)
            limlinks=[l for l in links if "." in l]
            for l in limlinks:
                if l not in allpages:
                    pagesToVisit = pagesToVisit + [l]
                    allpages.append(l)

            numberVisited = numberVisited +1

            for link in links:
                G.add_edge(url,link)

        except:
            print(" **Failed to parse page!**")

    return G,allpages
"""
"""
def getusrfolderfilelist(usr):
    '''
    Creates a dictionary for the user of their files and folders
    - To be changed into a system using a csv file to store links of the files
    '''

    filelist,listoffldrs=getpathlist(usr)

    fldr=packuserinfo(usr)["folder"]

    folderlist={}
    for foldername in listoffldrs:
        foldername=foldername.replace(fldr,"")
        if foldername not in folderlist and foldername != "":
            folderlist[foldername]=[]
        for filepath in filelist:
            filepathlist=filepath.replace(fldr,"").split("/")
            filename=filepathlist[-1]
            folderpathlist=filepathlist[:-1]
            folderpath=""
            for x in folderpathlist:
                folderpath+=(x+"/")

            if folderpath == foldername+"/":
                folderlist[foldername].append(filename)

    return folderlist
"""

def getusrfolderfilelistv2(usr):
    '''
    Gets a dictionary of user files
    '''
    usrdict=packuserinfov2(usr)

    profile=pd.read_csv(usrdict["usrprof"])
    folderlist={}

    for index,line in profile.iterrows():
        line=list(line)
        fldr=line[0]
        filenm=line[1]
        fileurl=line[2]

        if fldr not in folderlist:
            folderlist[fldr]=[[filenm,fileurl]]
        else:
            folderlist[fldr].append([filenm,fileurl])

    return folderlist

"""
def getpathlist(usr):
    '''
    gets file and folder path list for usr
    '''
    usrinfo=packuserinfo(usr)
    fldr=usrinfo["folder"]

    listoffldrs=[x[0].replace("\\","/") for x in os.walk(fldr)]

    completelist=[x.replace("\\","/") for x in glob.glob(fldr+"/*/**",recursive=True)]
    l2=[]
    for line in completelist:
        if line[-1]=="/":
            l2.append(line[:-1])
        else:
            l2.append(line)

    filelist=[x for x in l2 if x not in listoffldrs]

    return filelist,listoffldrs
"""

def filesfrommsg(msg):
    '''
    takes msg and checks for attachments and retrieves and returns urls
    '''

    attch= msg.attachments

    list_of_files=[]

    # go through message attachments and add to list
    if len(attch) != 0:
        for line in attch:
            fileurl=line["url"]
            filename=line["filename"]
            list_of_files.append((filename,fileurl))

    return list_of_files
