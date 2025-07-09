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
# Note-taking application

@csrf_exempt
def loginView(request):

    ###
    ### FLAW 1 - Broken Authentication -
    ###
    # fetch username & password
    user = request.POST.get('username', '')
    passw = request.POST.get('password', '')
    # user = request.GET.get('username', '')
    # passw = request.GET.get('password', '')

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
            #print("-- loginView TEST: cursor.fetchone() returns: None, request.GET/POST.username:", user, ", pu:", pu)
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
            data = cursor.execute("SELECT * FROM Notes where user='" + user + "'")
            #data = cursor.execute("SELECT * FROM Notes where user = ?", (user, ))
            notes = [d[1] for d in data.fetchall()]
        except sqlite3.OperationalError:
            print("-- Error: No notes for current user found in database (sqlite3.OperationalError), data:", data)
        finally:
            conn.close()
        
        return render(request, 'notes/notes.html', {'notes_list': notes})

    else:
        # Failed login attempt
        ###
        ### FLAW 3 - Insufficient Logging & Monitoring -
        ###
        #pass

        # # Print information
        inst = datetime.now()
        req_det = {'http_referer' : request.META.get('HTTP_REFERER'),
        'remote_addr' : request.META.get('REMOTE_ADDR'),
        'http_host' : request.META.get('HTTP_HOST'),
        'time' : '\t' + inst.isoformat(),
        'request_method' : request.META.get('REQUEST_METHOD'),
        'http_user_agent' : request.META.get('HTTP_USER_AGENT')}
        
        print("User and password didn't match\nRequest details:")
        [print(key,"\t", value) for (key,value) in req_det.items()]

    return render(request, 'notes/index.html')

# credentials when using auth:
# admin:S3cure_4dmin
# metoo:1bollocks



#### Manual mode views start here ####

###
### FLAW 4 - Security Misconfiguration - *** F4 ***
###
###  -- MANUAL --
# def addView(request):

#     # get current user from and connection to database
#     cUser = getCurrentUser()
#     conn, cursor = getConnAndCursorForNotes()

#     # add note, if not empty, to notes database and save them
#     if request.method == 'POST':
#         note = request.POST.get('note', '').strip()
#         if cUser == None:
#             print("-- addView: User: None")
#         print("note:", note, cUser)
#         if len(note) > 0 and cUser != None:
#             # save note to database, commit
#             ###
#             ### FLAW 2 - SQL Injection -
#             ###
#             #cursor.executescript("INSERT INTO Notes(content, user) VALUES('" + note + "','" + cUser + "')")
#             cursor.execute("INSERT INTO Notes(content, user) VALUES(?, ?)", (note, cUser))
#             conn.commit()

#     notes = getNotesForCurrent()
#     return render(request, 'notes/notes.html', {'notes_list': notes})


# ###
# ### FLAW 4 - Security Misconfiguration
# ###
# ### --- MANUAL --
# def eraseView(request):
#     ###
#     ### FLAW 6 - CSRF -
#     ###
#     #if request.method == 'POST':
#     if request.method == 'POST' or 'GET':
#         # empty previously saved list and assign empty list to session
#         notes = []
#         try:
#             cUser =  getCurrentUser()
#             conn, cursor = getConnAndCursorForNotes()
#             cursor.execute("DELETE FROM Notes WHERE user=?", (cUser,))
#             conn.commit()
#             conn.close()
#         except Exception as ex:
#             print("-- Error deleting data:", ex)

#     # Do we need an else -branch here, for legitimate app logic
#     #  when malformed request that is neither GET nor POST has been sent?
#     #  Make notes empty and render
    
#     return render(request, 'notes/notes.html', {'notes_list': notes})


# ###
# ### FLAW 4 - Security Misconfiguration -
# ###
# ### --- MANUAL ---
# ### Get all data from database, send to notes.html
# def allView(request):

#     data = ''
#     try:
#         conn, cursor = getConnAndCursorForNotes()
#         data = cursor.execute("SELECT * FROM Notes")
#     except Exception as ex:
#         print("-- Error in allView getting data from database:", ex)

#     all_notes = [item for item in data]

#     conn.close()
#     return render(request, 'notes/notes.html', {'notes_list': all_notes})

#### Manual mode views end here ####



#### Model views start here ####

###
### FLAW 4 - SECURITY MISCONFIGURATION -
###
### --- MODEL ---
#@csrf_exempt
@login_required
def addView(request):

    # _DEL_ # get previously saved notes from database
    # _DEL_ #notes = request.session.get('notes_list', [])
    # _DEL_ #notes = [n.content for n in Note.objects.filter(user=request.user)]

    # add note, if any, to session's notes and save them
    if request.method == 'POST':
        note = request.POST.get('note', '').strip()
        if len(note) > 0:
            modelNote = Note.objects.create(content=note, user=request.user)

    notes = [n.content for n in Note.objects.filter(user=request.user)]

    return render(request, 'notes/notes.html', {'notes_list': notes})


###
### FLAW 4 - SECURITY MISCONFIGURATION -
###
### -- MODEL --
#@login_required
def eraseView(request):
    
    notes = request.session.get('notes_list', [])
    # print('session.get(notes_list) length:', len(notes))
    # #print('request.session length:', len(request.session))
    # print('request.user:', request.user)

    if request.method == 'POST' or request.method == 'GET' :
        # empty previously saved list and assign empty list to session
        notes = []
        request.session['notes_list'] = []
        # empty current user's all Notes from database
        Note.objects.filter(user=request.user).delete()
    
    return render(request, 'notes/notes.html', {'notes_list': notes})


##
## FLAW 4 - Security Misconfiguration -
##
## --- MODEL ---
@csrf_exempt
def allView(request):

### FLAW 5 - Broken Access Control -
    # only allow access for admin
    if (request.user.username == 'admin'):
        data = Note.objects.all()
        notes = [note.content + '|' + note.user.username for note in data]
        return render(request, 'notes/notes.html', {'notes_list': notes})
    # otherwise send to login page
    else:
        return redirect('/')
# # ### FLAW 5 - Broken Access Control -
#     # allow access for all
#     data = Note.objects.all()
#     notes = [note.content + '|' + note.user.username for note in data]
#     return render(request, 'notes/notes.html', {'notes_list': notes})

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

    # users and passwords
    user1 = {'user': 'admin', 'password': 'admin' }
    user2 = {'user': 'user', 'password': 'password' }
    users = [user1, user2]

    for u in users:
#        print("Checking user", u['user'], ":", u['password'], "against", username, ":", password)
        if u['user'] == username and u['password'] == password:
#            print("User found")
            return True
#    print("No user found")
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
        # for item in data.fetchall():
        #     notes.append(item[1])
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


""" 
# FIX 2
# -- MANUAL --
@csrf_exempt
#@login_required
def indexView(request):

    # get previously saved notes from database

    # open connection
    conn, cursor = getConnAndCursorForNotes()

    # fetch all notes of user
    data = cursor.execute("SELECT * FROM Notes where user=" + request.GET.get('user'))

    # FIX 4
    # execute parameterized SQL to fetch all notes of user
    #data = cursor.execute("SELECT * FROM Notes where user_id = ?", (user, ))

    # MODEL
    #notes = Note.objects.filter(user=request.user)
    # MANUAL
    # filter user's notes
    # GET user FIRST!
    notes = [item for item in data.fetchall() if item[2] == user]
    # notes = []
    # for item in data:
    #     notes.append(item)
    #     print("TEST indexView -- ", request.GET.get('user'), item)

    # --TEST
    #print("notes:", len(notes), "items")

    return render(request, 'notes/index.html', {'notes_list': notes})
 """

# FIX 2
# -- MODEL --
#@csrf_exempt
# @login_required
# def indexView(request):
#     # get previously saved notes from database
#     # TODO fetch only user specific notes
#     #if request.user.is_authenticated:
#     #notes = request.session.get('notes_list', [])

#     # FIXME add .get
#     notes = Note.objects.filter(user=request.user)

#     return render(request, 'notes/index.html', {'notes_list': notes})


## Notes for notes FIXME
# !- need models: Note with content:text and user/userid:int
# !- check database and session saving with sqlite3 db.sqlite OR open it with DBeaver
# ?- CSRF:   Vuln: implement CSRF-disabling middleware, all the tags can(?) be in place
#           Fix: comment out disabling middleware
#  - skip the CSRF, user identification not wroking with models, block not working with manual
# !- SQL Injection: change user credentials to be saved to database
#   !- add credentials to database in database init script - NO NEED, using INSERT
#   -\ implement SQL query to use form data from lginView to check username and password
#   !- OR try to inject with INSERT, to be executed when loading 
#   - (eraseAll needs authentication, otherwise Injection is not fixed)
#    (-> move Flaw after models have been taken in use)
#     !- executescript -> execute (+ parameterized) will stop Injections from working
# !- Security Misconfiguration: add user credentials for models to init script
#  - no need, can be put in advance in the db, since vulnerable credentials are in source code
#
# !- All: remove fixX switches, fixes need to be commented out as per project instructions
