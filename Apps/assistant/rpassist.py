import discord
import os
from time import gmtime, strftime
import sys, traceback

from Bot import functions as fn

class  rpassistant(object):
    '''
    Daily RP Section Meta News Reporting
        News feed including:
            App approvals
            Activity Digest
            User Reports
            General Reminders
    User Profiles
        RP Participation List
        Character profiles (1st to make)
            App
            Inventory
            Status
        Current Summary Status
        To Do List Manager
        Reminder Function
    App Creator, Approval System, and Archives

    Additional notes:
        - RPs will be objects with some basic info, mainly links to OOC and IC
          as well as last active time info
        - Character Profiles will be objects with the above items

    '''
    def __init__(self,client,commandprefix,vnum):
        self.commandprefix=commandprefix #bot command prefix
        self.vnum=vnum #version number reference
        self.client=client #used here only to make sure the client object is available

        #load last state, if available.
        # this might need to go in the bot itself. pickling in the cmdmngr and loading the pickle in the bot.

        #get user information
        # user load system with file naming convention. need to go to Mobius_Users
        # userinfo=packuserinfo(usr)
        # usersubfolder=userinfo["folder"]+"/rpassistant"

        #Server status
        # This will be a folder Mobius_Server. Will also need logs_Server
        serverlogsfolder="./Mobius_logs/Logs_Server/"

    def user_profile_creator(userinfo):
        '''
        Creates user profile.
        Reference register function (Bot.functions line 138)
        '''
