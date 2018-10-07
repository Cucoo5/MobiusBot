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
        Character profiles
            App
            Inventory
            Status
        Current Summary Status
        To Do List Manager
        Reminder Function
    App Creator, Approval System, and Archives
    '''
    def __init__(self,client,commandprefix,vnum):
        self.commandprefix=commandprefix #bot command prefix
        self.vnum=vnum #version number reference
        self.client=client #used here only to make sure the client object is available

        #load last state, if available.
        
