from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from .models import Note
import sqlite3

# Cyber Security Base
# Project I
# Notes: Note-taking application

@csrf_exempt
def loginView(request):

    ###
    ### FLAW 1 - Broken Authentication -
    ###
    # fetch username & password
    # user = request.POST.get('username', '')
    # passw = request.POST.get('password', '')
    user = request.GET.get('username', '')
    passw = request.GET.get('password', '')

    # verify username and password
    if (userFound(username=user, password=passw)):
        # user and password correct, fetch & show notes

        # open connection
        conn, cursor = getConnAndCursorForNotes()
        data = []

        # update current user to database: delete any previous, save current
        prevuserC = cursor.execute("SELECT * FROM CurrentUser")
        pu = prevuserC.fetchone()

        # has the page been accessed without logging in first
        if pu == None and user == None:
            conn.close()
            # return to login screen
            return render(request, 'notes/index.html')
        else:
            # delete current user
            data = cursor.execute("DELETE FROM CurrentUser")

        cursor.execute("INSERT INTO CurrentUser VALUES(?)", (user,))
        conn.commit()

        # try to get current user's notes from database
        notes = []
        try:
            data = cursor.execute("SELECT * FROM Notes where user = ?", (user, ))
            notes = [d[1] for d in data.fetchall()]
        except sqlite3.OperationalError:
            print("-- Error loginView: No notes for current user found in database (sqlite3.OperationalError), data:", data)
        finally:
            conn.close()
        
        return render(request, 'notes/notes.html', {'notes_list': notes})

    else:
        # Failed login attempt
        ###
        ### FLAW 3 - Insufficient Logging & Monitoring -
        ###
        pass

        # # Print information
        # inst = datetime.now()
        # req_det = {'http_referer' : request.META.get('HTTP_REFERER'),
        # 'remote_addr' : request.META.get('REMOTE_ADDR'),
        # 'http_host' : request.META.get('HTTP_HOST'),
        # 'time' : '\t' + inst.isoformat(),
        # 'request_method' : request.META.get('REQUEST_METHOD'),
        # 'user_agent' : request.META.get('HTTP_USER_AGENT')}
        
        # print("-- User and password didn't match --\nRequest details:")
        # [print(key,"\t", value) for (key,value) in req_det.items()]

    return render(request, 'notes/index.html')



#### Manual mode views start here ####

###
### FLAW 4 - Security Misconfiguration -
###
###  -- MANUAL --
### Add note as current user's to database
def addView(request):

    # get current user from and connection to database
    cUser = getCurrentUser()
    conn, cursor = getConnAndCursorForNotes()

    # add note, if not empty, to notes database and save it
    if request.method == 'POST':
        note = request.POST.get('note', '').strip()
        if cUser == None:
            print("-- addView: User: None")
        print("note:", note, cUser)
        if len(note) > 0 and cUser != None:
            # save note to database, commit
            ###
            ### FLAW 2 - SQL Injection -
            ###
            cursor.executescript("INSERT INTO Notes(content, user) VALUES('" + note + "','" + cUser + "')")
            #cursor.execute("INSERT INTO Notes(content, user) VALUES(?, ?)", (note, cUser))
            conn.commit()

    notes = getNotesForCurrent()
    return render(request, 'notes/notes.html', {'notes_list': notes})


###
### FLAW 4 - Security Misconfiguration
###
### --- MANUAL --
### Erase current user's notes from database
def eraseView(request):

    #if request.method == 'POST':
    if request.method == 'POST' or 'GET':
        # empty previously saved list and assign empty list to session
        notes = []
        try:
            cUser =  getCurrentUser()
            conn, cursor = getConnAndCursorForNotes()
            cursor.execute("DELETE FROM Notes WHERE user=?", (cUser,))
            conn.commit()
            conn.close()
        except Exception as ex:
            print("-- Error deleting data:", ex)

    return render(request, 'notes/notes.html', {'notes_list': notes})


###
### FLAW 4 - Security Misconfiguration -
###
### --- MANUAL ---
### Get all data from database, send to notes.html
def allView(request):

    data = ''
    try:
        conn, cursor = getConnAndCursorForNotes()
        data = cursor.execute("SELECT * FROM Notes")
    except Exception as ex:
        print("-- Error in allView getting data from database:", ex)

    all_notes = [item for item in data]

    conn.close()
    return render(request, 'notes/notes.html', {'notes_list': all_notes})

#### Manual mode views end here ####



#### Model views start here ####

# ###
# ### FLAW 4 - SECURITY MISCONFIGURATION -
# ###
# ### --- MODEL ---
# ### Add note as current user's to database
# #@csrf_exempt
# @login_required
# def addView(request):

#     # add note, if any, to database
#     if request.method == 'POST':
#         note = request.POST.get('note', '').strip()
#         if len(note) > 0:
#             modelNote = Note.objects.create(content=note, user=request.user)

#     notes = [n.content for n in Note.objects.filter(user=request.user)]

#     return render(request, 'notes/notes.html', {'notes_list': notes})


# ###
# ### FLAW 4 - SECURITY MISCONFIGURATION -
# ###
# ### -- MODEL --
# #@login_required
# def eraseView(request):
    
#     notes = request.session.get('notes_list', [])

#     if request.method == 'POST' or request.method == 'GET' :
#         # empty previously saved list and assign empty list to session
#         notes = []
#         request.session['notes_list'] = []
#         # empty current user's all Notes from database
#         Note.objects.filter(user=request.user).delete()
    
#     return render(request, 'notes/notes.html', {'notes_list': notes})


# # ###
# # ### FLAW 4 - Security Misconfiguration -
# # ###
# # ### --- MODEL ---
# # ### Get all data from database, send to notes.html
# @csrf_exempt
# def allView(request):

# ###
# ### FLAW 5 - Broken Access Control -
# ###
#     # only allow access for admin
#     if (request.user.username == 'admin'):
#         data = Note.objects.all()
#         notes = [note.content + '|' + note.user.username for note in data]
#         return render(request, 'notes/notes.html', {'notes_list': notes})
#     # otherwise send to login page
#     else:
#         return redirect('/')
# # # ### FLAW 5 - Broken Access Control -
# #     # allow access for all
# #     data = Note.objects.all()
# #     notes = [note.content + '|' + note.user.username for note in data]
# #     return render(request, 'notes/notes.html', {'notes_list': notes})

#### Model views end here ####





# When logging out of manual mode, remove current user from database and open loginView
def logoutView(request):
    try:
        conn, cursor = getConnAndCursorForNotes()
        cursor.execute("DELETE FROM CurrentUser")
        conn.commit()
        conn.close()
    except Exception as ex:
        print("-- Error removing current user:", ex)

    return render(request, 'notes/index.html')


####################################
# Helper functions for manual mode #
####################################

# check user credentials
def userFound(username, password):

    # credentials when using auth.models login:
    # admin:S3cure_4dmin
    # metoo:YouThree-four

    # users and passwords
    user1 = {'user': 'admin', 'password': 'admin' }
    user2 = {'user': 'user', 'password': 'password' }
    users = [user1, user2]

    for u in users:
        if u['user'] == username and u['password'] == password:
            return True
    return False


# get username of logged-in user
def getCurrentUser():

    user = ''
    try:
        conn, cursor = getConnAndCursorForNotes()
        data = cursor.execute("SELECT * FROM CurrentUser")
        user = data.fetchone()
        conn.close()
        return user[0]
    except Exception as ex:
        print("-- Error getCurrentUser:", ex)
        conn.close()
        return None


# retrieve notes from database for current user
def getNotesForCurrent():

    notes = []
    try:
        conn, cursor = getConnAndCursorForNotes()
        cUser = getCurrentUser()
        data = cursor.execute("SELECT * FROM Notes WHERE user=?", (cUser,))
        notes = [item[1] for item in data.fetchall()]
    except Exception as ex:
        print("-- Error getNotesForCurrent:", ex)
    finally:
        conn.close()

    return notes


# return connection to and cursor to execute scripts in database
def getConnAndCursorForNotes():

    conn = sqlite3.connect("notes.sqlite")
    cursor = conn.cursor()
    return (conn, cursor)
