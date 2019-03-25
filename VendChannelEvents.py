import csv
from VendApi import *
from VendChannelEventsGUI import *
from GitHubApi import *
import re
import threading
import queue
import tkinter
import CsvUtil as cu
import traceback
import os
import time
import textwrap
import getpass
import json
import GitFeedbackIssue as gitfeedback
from os.path import expanduser
from datetime import datetime
from ToolUsageSheets import *

VERSION_TAG = '1.1'
APP_FUNCTION = 'VendChannelEvents'
ACTIONS = []

#gitApi = None
USER = getpass.getuser()

gui = None
api = None
retrieveFilepath = ""
THREAD_COUNT = 1
results = None


def startProcess(bulkDelGui):
    """
        The entry point to begin retrieving customers to delete and process the
        bulk delete task. Handles all the basic error checks and feedback to the
        user through the GUI status message/bar, before creating API class.
    """
    global gui
    gui = bulkDelGui
    if not gui.entriesHaveValues():
        ## error
        gui.setStatus("Please have values for prefix / token / ticket #.")
        gui.setReadyState()
        return

    '''
    if not gui.isChecklistReady():
        gui.setStatus("Please make sure checklist is completed...")
        gui.setReadyState()
        return
    '''
    gui.setStatus("")

    gui.resetTreeview()

    try:

        api = VendApi(gui.getPrefix(), gui.getToken())

        params = getQueryParams(gui)

        channels = api.getChannels()

        if channels is None:
            gui.setStatus("Could not retrieve channel. Please check prefix and token (expiry).")
            gui.setReadyState()
            return
        print(channels)
        chanEventId = channels[0]['id']
        channelEvents = api.getChannelEvents(chanEventId, params=params)

        #print(channelEvents)

        chanEventVals = getChannelEvents(channelEvents)

        displayEvents(chanEventVals)

        addActionEvents(USER, APP_FUNCTION, str(datetime.now()))

        #print(gui.getEventLevel())
        gui.setReadyState()
    except Exception as e:
        issue = gitApi.createIssue(title=f"[{USER}]{str(e)}", body=traceback.format_exc(), assignees=['minstack'], labels=['bug']).json()
        gui.showError(title="Crashed!", message=f"Dev notified and assigned to issue:\n{issue['html_url']}")

def addActionEvents(user, app, date):

    details = f"Level:{gui.getEventLevel()},EntityType:{gui.getEntityType()},EntityId:{gui.getEntityId()}"

    toolusage.writeRow(**{
        "user" : user,
        "appfunction" : app,
        "completedon" : date,
        "prefix" : gui.getPrefix(),
        "ticketnum" : gui.getTicketNum(),
        "details" : details
    })
    '''toolusage.saveRowLocally(**{
        "user" : user,
        "appfunction" : app,
        "completedon" : date,
        "prefix" : gui.getPrefix(),
        "ticketnum" : "3234234"
    })'''


def getQueryParams(gui):


    entryLevel = gui.getEventLevel()
    entityId = gui.getEntityId()
    entitytype = gui.getEntityType()

    params = {}

    if entryLevel != "all":
        params['level'] = entryLevel

    if entitytype != "all":
        params['entity_type'] = entitytype

    if len(entityId) > 0:
        params['entity_id'] = entityId

    return params

def wrap(string, length=16):
    return '\n'.join(textwrap.wrap(string, length))

def displayEvents(eventVals):

    attributes = ["created_at", "action", "entity_type", "entity_id", "unwrapped_error"]

    wrapped_error = []

    for error in eventVals['unwrapped_error']:

        temp = ""

        if len(error) > 0:
            temp = wrap(error, 65)

        wrapped_error.append(temp)

    zippedList = zip(eventVals['created_at'], \
                        eventVals['action'], \
                        eventVals['entity_type'], \
                        eventVals['entity_id'], \
                        wrapped_error)



    gui.addRowsToTreeview(zippedList)


def getChannelEvents(channelEvents):

    attributes = ["created_at", "action", "entity_type", "entity_id", "unwrapped_error"]
    attr_values = {
        "created_at" : [],
        "action" : [],
        "entity_type" : [],
        "entity_id" : [],
        "unwrapped_error" : []
    }

    #print(channelEvents)

    for e in channelEvents:
        attr_values['created_at'].append(e['created_at'])
        attr_values['action'].append(e['action'])
        attr_values['entity_type'].append(e['entity_type'])
        attr_values['entity_id'].append(e['entity_id'])

        data = e['data']
        unwrapped_error = ""
        #print(data)
        if data:
            unwrapped_error = data.get('unwrapped_error', "")

        attr_values['unwrapped_error'].append(unwrapped_error)

    global results
    results = attr_values

    return attr_values

def exportToCsv():

    global results

    if results is None:
        gui.setStatus("There are no results to export.")
        return

    for key in results:
        results[key].insert(0, key)

    print(results)

    zipped = zip(results['created_at'], \
                    results['action'], \
                    results['entity_type'], \
                    results['entity_id'], \
                    results['unwrapped_error'])

    filepath = cu.writeListToCSV(output=zipped, title=f'channels-ticket{gui.getTicketNum()}', prefix=gui.getPrefix())

    gui.setStatus(f"Exported to {filepath}.")

def downloadUpdates(mainGui):


    latestrelease = gitApi.getLatestReleaseJson()

    tag = latestrelease.get('tag_name', None)

    #no releases
    if tag is None:
        return False

    if latestrelease['tag_name'] <= VERSION_TAG:
        return False

    #download latest update
    userdesktop = expanduser('~') + '/Desktop'
    filename = gitApi.downloadLatestRelease(path=userdesktop, extract=True)
    updatedescription = latestrelease['body']

    mainGui.showMessageBox(title=f"Updates v{latestrelease['tag_name']}", \
                            message=f"Downloaded latest version to your desktop: \
                                        {filename[:-4]}\n\nYou may delete this version.\
                                        \n\nUpdate Details:\n{updatedescription}")

    return True

def loadData():
    global DATA

    with open('data.json') as f:
        DATA = json.load(f)

    global gitApi

    #print(f"{data['owner']}: {data['repo']} : {data['ghtoken']}")

    gitApi = GitHubApi(owner=DATA['owner'], repo=DATA['repo'], token=DATA['ghtoken'])

    global toolusage
    toolusage = ToolUsageSheets(credsfile=DATA['credjson'], \
                                sheetId=DATA['sheetId'], \
                                sheetName=DATA['sheetName'])

def openFeedbackDialog():
    gitfeedback.main()

def onClose():
    toolusage.writeLocallySavedRows()
    gui.destroy()


if __name__ == "__main__":
    loadData()
    try:
        #global gui
        gui = VendChannelEventsGUI(callback=startProcess)
        gui.setExportCsvCommand(exportToCsv)
        gui.setVersion(VERSION_TAG)

        if not downloadUpdates(gui):
            #gui.setOnClose(onClose)
            gui.setFeedBackCommand(openFeedbackDialog)
            gui.main()

    except Exception as e:
        issue = gitApi.createIssue(title=f"[{USER}]{str(e)}", body=traceback.format_exc(), assignees=['minstack'], labels=['bug']).json()
        gui.showError(title="Crashed!", message=f"Dev notified and assigned to issue:\n{issue['html_url']}")
