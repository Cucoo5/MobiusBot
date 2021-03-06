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

    Assign and manage roles


    Additional notes:
        - RPs will be objects with some basic info, mainly links to OOC and IC
          as well as last active time info
        - Character Profiles will be objects with the above items

    '''
    def __init__(self,client,commandprefix,vnum):
        self.commandprefix=commandprefix #bot command prefix
        self.vnum=vnum #version number reference
        self.client=client #used here only to make sure the client object is available

        #get user information


        #Server status
        # This will be a folder Mobius_Server. Will also need logs_Server
        serverlogsfolder="./Mobius_logs/Logs_Server/"

    def user_role_assignment(usr,role):
        '''
        
        '''
