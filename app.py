import os
import random
from flask import render_template, request, Flask
from werkzeug.exceptions import NotFound, InternalServerError, MethodNotAllowed, BadRequest
import DataBase as db
from track import detect
from motion_heatmap import heatmap
import pandas as pd
import json
import plotly
import plotly.express as px
from datetime import date

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from DataBase import setup_db
from flask_cors import CORS



MYDIR = os.path.dirname(__file__)




## ============================================= Dashboard ============================================ ##

def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)



    @app.route('/', methods=['GET','POST'])
    def index():
       
        try:
            nbTotal = 0
            defaultDate = []
            username = request.form['username']
            displayName =  db.displayname(username)
            user = username.split(' ')[0]
            password = request.form['password']
            currentDateOrg  = date.today()
            currentDate = str(currentDateOrg.strftime("%A %d %b %Y"))
           
            defaultDate = db.defaultDate(username,"all sites")
          
            userSites = db.UserSites(username, "all")

            email = db.getEmail(username)

            if(db.LoginChecker(username , password)):
                if defaultDate != [] and defaultDate != None:
                    nbTotal = db.totalNumberOfVistors("all sites", username, defaultDate[0], defaultDate[1])
                else: 
                    if userSites == [] or userSites == None:
                        userSites = ""
                        currentSite = "There is no site's"
                    else:
                        currentSite = "all sites"  
                    return render_template('dashboard.html', currentDate=currentDate ,startD = currentDateOrg, endD = currentDateOrg, nbTotal=nbTotal, avgSpentm=0,
                    avgSpents=0,mostVistors=0, fewestVistors=0,  graph="", graphh="",
                    M_DAY = "", F_DAY = "", userSites=userSites, currentSite=currentSite, username=username, user=user, displayName=displayName, email=email)
           
                
                avgSpent = db.AvgTimeSpent("all sites", username, defaultDate[0], defaultDate[1])
                avgSpentm = int(avgSpent / 60)
                avgSpents = int(( (avgSpent / 60) - int(avgSpent / 60) ) * 100)
                mostVistors = db.SiteWithMaxVistors(username, defaultDate[0], defaultDate[1])
                fewestVistors = db.SiteWithFewestVistors(username, defaultDate[0], defaultDate[1])
                mostDays = db.FiveMostDaysOfVistors(username, "all sites", defaultDate[0], defaultDate[1])
                fewestDays = db.FiveFewestDaysOfVistors(username, "all sites", defaultDate[0], defaultDate[1])
                mostDays, fewestDays = dateFormat(mostDays, fewestDays)
                userSites = db.UserSites(username, "all")
                userSites.sort()
                if userSites == [] or userSites == None:
                    userSites = ""
                graph, graphh = getGraphs(username, "all sites", defaultDate[0], defaultDate[1])

                siteNames, images = db.displayHeatMap(username, "all sites", defaultDate[0], defaultDate[1])
      

                return render_template('dashboard.html', images=images, siteNames=siteNames, currentDate=currentDate ,startD = defaultDate[0], endD = defaultDate[1],nbTotal=nbTotal, avgSpentm=avgSpentm,
                avgSpents = avgSpents,mostVistors=mostVistors, fewestVistors=fewestVistors,
                M_DAY = mostDays, F_DAY = fewestDays, userSites=userSites, currentSite="all sites", username=username, user=user,
                graph=graph, graphh=graphh, displayName=displayName, email=email)
            else:
                return render_template('login.html', checkLogin=0)

        except Exception as e:      
            print(str(e))
            return render_template('login.html')
       
      


    
    @app.route('/register' , methods=['GET','POST'])
    def register():
        return render_template('register.html', alreadyExists="")

    @app.route('/reset' , methods=['POST']) 
    def reset():  

        return render_template('reset.html') 

    @app.route('/account' , methods=['POST']) 
    def account(): 
        email = request.form['email']
        if db.EmailChecker(email):
            code = random.randint(1000,9999)
            send_code(email, code)
            return render_template('OTP Reset.html', email=email, code=code)    
        else:
            return render_template('reset.html')

    @app.route('/ResetPassword' , methods=['POST']) 
    def ResetPassword(): 
         email = request.form['email']
         return render_template('reset2.html', email=email)




    @app.route('/ResetAccount' , methods=['POST']) 
    def resetAccount(): 
        email = request.form['email']
        password = request.form['password']
        cpassword = request.form['cpassword']
        
        if password == cpassword:
            db.PasswordReset(email, password)
            return render_template('login.html')    
        else:
            return render_template('reset2.html')
     
    @app.route('/Register' , methods=['POST']) 
    def Register():
          return render_template('register.html', alreadyExists = "")

    @app.route('/Info' , methods=['POST']) 
    def Info(): 
        fName = request.form['firstName']
        lName = request.form['lastName']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        cpassword = request.form['cpassword']
           
        code = random.randint(1000,9999)
        send_code(email, code)
        return render_template('OTP.html', code=code, fName=fName, lName=lName, username=username, email=email, password=password, cpassword=cpassword)
           


    @app.route('/NewUser' , methods=['POST']) 
    def NewUser(): 
        fName = request.form['firstName']
        lName = request.form['lastName']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        cpassword = request.form['cpassword']
        code = request.form['code']
        code1 = request.form['code1']
        code2= request.form['code2']
        code3 = request.form['code3']
        code4 = request.form['code4']

        if (password == cpassword) and (fName != "") and (lName != "") and (username != "") and (email != "") and (password != "") and (cpassword != ""):
            if (code1+code2+code3+code4) == code:
                if db.addToUser(username, fName+" "+lName, email, password):
                    return render_template('login.html')
                else:
                    return render_template('register.html', alreadyExists = "This user already exists !!")
        return render_template('register.html', alreadyExists = "This user already exists !!")


    @app.route('/check_username', methods=['POST'])
    def check_username():
        if request.method == 'POST':
            username = request.form['username']
            if  db.UserChecker(username) == False:
                print('{ "html":"Ok"}')
                msg =  '{ "html":"Ok"}'
                msghtml = json.loads(msg)
                return msghtml["html"]
            else:   
                print('{ "html":"No found"}')
                msg =  '{ "html":"No found"}'
                msghtml = json.loads(msg)
                return msghtml["html"] 


    @app.route('/check_email', methods=['POST'])
    def email_username():
        if request.method == 'POST':
            email = request.form['email']
            if  db.EmailChecker(email) == False:
                msg =  '{ "html":"Ok"}'
                msghtml = json.loads(msg)
                return msghtml["html"] 
            else:   
                msg =  '{ "html":"No found"}'
                msghtml = json.loads(msg)
                return msghtml["html"]                 

    @app.route('/dashboard', methods=['GET','POST'])
    def dashboard():
        currentDateOrg  = date.today()
        currentDate = str(currentDateOrg.strftime("%A %d %b %Y"))
        username = request.form['username']
        email = db.getEmail(username)
        displayName =  db.displayname(username)

        currentSite = request.form['currentSite']
        click = currentSite.lower()
        user = request.form['user']
        print("kkkkkkkkk == ",currentSite)
        addDate  = date.today()
        defaultDate = db.defaultDate(username, click)
        nbTotal = 0
        if defaultDate != None:
            startD = defaultDate[0]
            endD = defaultDate[1]
            nbTotal = db.totalNumberOfVistors(click, username, startD, endD)
            avgSpent = db.AvgTimeSpent(click, username, startD, endD)
            avgSpentm = int(avgSpent / 60)
            avgSpents = int(( (avgSpent / 60) - int(avgSpent / 60) ) * 100)
            if currentSite != "all sites":
                mostVistors = currentSite
                fewestVistors = currentSite
            else:
                mostVistors = db.SiteWithMaxVistors(username, startD, endD)
                fewestVistors = db.SiteWithFewestVistors(username, startD, endD)
            mostDays = db.FiveMostDaysOfVistors(username, click, startD, endD)
            fewestDays = db.FiveFewestDaysOfVistors(username, click, startD, endD)
            mostDays, fewestDays = dateFormat(mostDays, fewestDays)
            graph, graphh = getGraphs(username, click, startD, endD)
        else:
            startD = addDate
            endD = addDate
            avgSpent = 0
            avgSpentm = 0
            avgSpents = 0
            mostVistors = 0
            fewestVistors = 0
            mostDays = 0
            fewestDays = 0
            mostDays, fewestDays = 0, 0
            graph, graphh = 0,0
        userSites = db.UserSites(username, "all")
        if userSites == [] or userSites == None:
            userSites = ""
        print(nbTotal)    

        if nbTotal == None :
            nbTotal = 0
        
        siteNames, images = db.displayHeatMap(username, click, startD, endD)

        print("sites Names:",siteNames)
        print("sites Images:",images)

        print("Emaillllll:",email)

        return render_template('dashboard.html',images=images, siteNames=siteNames, currentDate=currentDate ,startD = startD, endD = endD, nbTotal=nbTotal, avgSpentm=avgSpentm,
                avgSpents = avgSpents,mostVistors=mostVistors, fewestVistors=fewestVistors,
                M_DAY = mostDays,F_DAY = fewestDays,currentSite=click, username=username, userSites=userSites, user=user, graph=graph, graphh=graphh,
                 displayName=displayName, email=email)


    @app.route('/select-management', methods=['GET','POST'])
    def select_management():
        form = request.form
        username = form["select"]
        email = db.getEmail(username)
        displayName =  db.displayname(username)
        currentSite = form["click"]
        click = currentSite.lower()
        userSites = form["userSites"]
        defaultDate = db.defaultDate(username, click)
        if defaultDate != None:
            startD = defaultDate[0]
            endD = defaultDate[1]
        else:
            startD, endD =  date.today(),  date.today()
        currentDate  = date.today()
        currentDate = str(currentDate.strftime("%A %d %b %Y"))
        userSites = getSites(userSites)
        if userSites == [] or userSites == None:
            userSites = ""
        user = username.split(' ')[0]

        if click[0] == " ":
            click = click[1:]

        nbTotal = db.totalNumberOfVistors(click, username, startD, endD)
        if nbTotal == None:
            nbTotal = 0
        if nbTotal == 0:
            return render_template('dashboard.html', currentDate=currentDate ,startD = startD, endD = endD, nbTotal=0, avgSpentm=0,
            avgSpents=0,mostVistors=0, fewestVistors=0,
            M_DAY = "", F_DAY = "", userSites=userSites, currentSite=click, username=username, user=user, displayName=displayName, email=email)
        else:
       
            avgSpent = db.AvgTimeSpent(click, username, startD, endD)
            avgSpentm = int(avgSpent / 60)
            avgSpents = int(( (avgSpent / 60) - int(avgSpent / 60) ) * 100)
            if currentSite != "All sites":
                mostVistors = currentSite
                fewestVistors = currentSite
            else:
                mostVistors = db.SiteWithMaxVistors(username, startD, endD)
                fewestVistors = db.SiteWithFewestVistors(username, startD, endD)
            mostDays = db.FiveMostDaysOfVistors(username, click, startD, endD)
            fewestDays = db.FiveFewestDaysOfVistors(username, click, startD, endD)
            mostDays, fewestDays = dateFormat(mostDays, fewestDays)
            graph, graphh = getGraphs(username, click, startD, endD)

            siteNames , images  = db.displayHeatMap(username, click, startD, endD)
            print("detlilssss",username, click, startD, endD)
            return render_template('dashboard.html', images=images, siteNames=siteNames, currentDate=currentDate ,startD = startD, endD = endD, nbTotal=nbTotal, avgSpentm=avgSpentm,
                avgSpents = avgSpents,mostVistors=mostVistors, fewestVistors=fewestVistors,
                M_DAY = mostDays,F_DAY = fewestDays,currentSite=click, username=username, userSites=userSites, user=user, graph=graph, graphh=graphh, displayName=displayName, email=email)




    @app.route('/filter', methods=['GET','POST'])
    def filter_date():
        start_date = request.form['Date1']
        end_date = request.form['Date2']
        username = request.form['username']
        email = db.getEmail(username)
        displayName =  db.displayname(username)
        currentSite = request.form['currentSite']
        currentSite = currentSite.lower()
        currentDate = request.form['currentDate']
        clickFilter = ""
        userSites = db.UserSites(username, "all")
        if userSites == []:
            userSites = ""
        print("userSites", userSites)
        user = username.split(' ')[0]
        
        if start_date == "" or end_date == "":
            defaultDate = db.defaultDate(username, currentSite)
            start_date = defaultDate[0]
            end_date = defaultDate[1]
            clickFilter = "True"
        nbTotal = db.totalNumberOfVistors(currentSite, username, start_date, end_date)
        if nbTotal == None:
            clickFilter = "False"
            return render_template('dashboard.html', currentDate=currentDate ,startD = start_date, endD = end_date, nbTotal=0, avgSpentm=0,
            avgSpents=0,mostVistors=0, fewestVistors=0,
            M_DAY = "", F_DAY = "", userSites=userSites, currentSite=currentSite, username=username, user=user, displayName=displayName, email=email)

        avgSpent = db.AvgTimeSpent(currentSite, username, start_date, end_date)
        avgSpentm = int(avgSpent / 60)
        avgSpents = int(( (avgSpent / 60) - int(avgSpent / 60) ) * 100)
        mostVistors = db.SiteWithMaxVistors(username, start_date, end_date)
        fewestVistors = db.SiteWithFewestVistors(username,start_date, end_date)
        mostDays = db.FiveMostDaysOfVistors(username, currentSite, start_date, end_date)
        fewestDays = db.FiveFewestDaysOfVistors(username, currentSite, start_date, end_date)
        mostDays, fewestDays = dateFormat(mostDays, fewestDays)
        userSites = db.UserSites(username, "all")
        userSites.sort()
        if userSites == []:
            userSites = ""
        graph, graphh = getGraphs(username, currentSite, start_date, end_date)

        siteNames, images = db.displayHeatMap(username, "all sites", start_date, end_date)
        return render_template('dashboard.html', siteNames=siteNames, images=images, currentDate=currentDate ,startD = start_date, endD = end_date, nbTotal=nbTotal, avgSpentm=avgSpentm,
        avgSpents = avgSpents,mostVistors=mostVistors, fewestVistors=fewestVistors,
        M_DAY = mostDays, F_DAY = fewestDays, userSites=userSites, currentSite=currentSite, username=username, user=user, graph=graph, graphh=graphh, clickFilter=clickFilter, displayName=displayName, email=email)

        
    ## ======================================================================================================= ##


    @app.route('/video-management', methods = ['GET', 'POST'])
    def video_management():
        username = request.form['username']
        displayName =  db.displayname(username)
        currentSite = request.form['currentSite']
        currentSite = currentSite.lower()

        currentDate = request.form['currentDate']
        addDate  = date.today()
        user = request.form['user']
        userSites = db.UserSites(username, "all")
        
        if userSites == []:
            userSites = ""

        siteName, videoAndDate = db.VideoName_with_siteName_List(username)



        return render_template('dashboard-2.html', currentDate=currentDate ,currentSite=currentSite, addDate=addDate, username=username, userSites=userSites,
                 user=user,siteName=siteName, videoAndDate=videoAndDate, displayName=displayName)



    @app.route('/upload', methods = ['GET', 'POST'])
    def upload_file():
        username = request.form['username']
        displayName =  db.displayname(username)
        user = username.split(' ')[0]
        currentSite = request.form['currentSite']
        currentSite = currentSite.lower()
        selectedSite = request.form['selectedSite']
        sdatetime = request.form['sdatetime']
        addDate  = date.today()
        userSites = db.UserSites(username, "all")
        file = request.files['file']

        
        file2 = str(file)
        ind = file2.index("/") + 1
        exten = ""
          
        while True:
            if file2[ind] != "\'":
                exten = exten + file2[ind]
                ind = ind + 1
            else:
                break   
          
        file.save(os.path.join(MYDIR + "/video." + exten ))
        countPeople, avgSpent = detect("video." + exten)
        videoId = db.getVideoId()
        heatMap = heatmap("video." + exten, videoId)
        print("file name",file.name)
        dir_path = "\static\images\\"+str(videoId)+".jpg"
        print("path",dir_path)
        checkVideo = db.addToVideo(selectedSite, len(countPeople), avgSpent, sdatetime ,dir_path,file.filename)
        siteName, videoAndDate = db.VideoName_with_siteName_List(username)
        
        return render_template('dashboard-2.html',currentSite=currentSite, addDate=addDate, username=username, userSites=userSites,
                 user=user, siteName=siteName, videoAndDate=videoAndDate,checkVideo=checkVideo, displayName=displayName)




    @app.route('/edit-video', methods = ['GET', 'POST'])
    def edit_video():
        username = request.form['username']
        displayName =  db.displayname(username)
        user = request.form['user']
        currentSite = request.form['currentSite']
        currentSite = currentSite.lower()
        userSites =  db.UserSites(username,"all")
        selectedVideoName = request.form['selectedVideoName']
        selectedVideoName = selectedVideoName.split(' |')[0]
        print("selected Video Name",selectedVideoName)
       

        enteredVideoName = request.form['enteredVideoName']
        print("entered Video Name",enteredVideoName)
        if enteredVideoName != "":
            db.update_videoName(selectedVideoName, enteredVideoName)

        enteredVideoDate = request.form['enteredVideoDate']
        print(enteredVideoDate,selectedVideoName)
        if enteredVideoDate != "":
            db.update_date_in_Video(enteredVideoDate, selectedVideoName)

        preSite = request.form['preSite']
        MoveSite = request.form['MoveSite']

        print("pre Site ",preSite)
        print("Move Site ",MoveSite)
        if enteredVideoDate == "" and selectedVideoName != "":
            db.update_site_in_Video(preSite, MoveSite, selectedVideoName)


        checkDeleteVideo = request.form['checkDeleteVideo']

        if selectedVideoName != "" and checkDeleteVideo == "true":
            db.removeVideo(selectedVideoName)

   
        addDate  = date.today()
        
        
        siteName, videoAndDate = db.VideoName_with_siteName_List(username)


        
        return render_template('dashboard-2.html', siteName=siteName, userSites=userSites, videoAndDate=videoAndDate, currentSite=currentSite, addDate=addDate, username=username,  user=user, displayName=displayName)





    ## ======================================================================================================= ##

    @app.route('/site-management', methods = ['GET', 'POST'])
    def site_management():
        currentDateOrg  = date.today()
        currentDate = str(currentDateOrg.strftime("%A %d %b %Y"))
        username = request.form['username']
        displayName =  db.displayname(username)
        currentSite = request.form['currentSite']
        currentSite = currentSite.lower()
        user = request.form['user']
        
        addDate  = date.today()
        defaultDate = db.defaultDate(username, currentSite)
        nbTotal = 0
        if defaultDate != None:
            startD = defaultDate[0]
            endD = defaultDate[1]
            nbTotal = db.totalNumberOfVistors(currentSite, username, startD, endD)
            avgSpent = db.AvgTimeSpent(currentSite, username, startD, endD)
            avgSpentm = int(avgSpent / 60)
            avgSpents = int(( (avgSpent / 60) - int(avgSpent / 60) ) * 100)
            mostVistors = db.SiteWithMaxVistors(username,startD, endD)
            fewestVistors = db.SiteWithFewestVistors(username, startD, endD)
            mostDays = db.FiveMostDaysOfVistors(username, currentSite, startD, endD)
            fewestDays = db.FiveFewestDaysOfVistors(username, currentSite, startD, endD)
            mostDays, fewestDays = dateFormat(mostDays, fewestDays)
            graph, graphh = getGraphs(username, currentSite, startD, endD)
        else:
            startD = addDate
            endD = addDate
            avgSpent = 0
            avgSpentm = 0
            avgSpents = 0
            mostVistors = 0
            fewestVistors = 0
            mostDays = 0
            fewestDays = 0
            mostDays, fewestDays = 0, 0
            graph, graphh = 0,0
        userSites = db.UserSites(username, "all")
        if userSites == [] or userSites == None:
            userSites = ""
            currentSite = "all sites"
            
        print(nbTotal)    

        if nbTotal == None :
            nbTotal = 0



        adminSite = db.UserSites(username, "Admin")
        userSite =  db.UserSites(username, "User")
        
        pendingSites = db.UserPendingSites(username)



        adminAndUsers = []
        for x in adminSite:
            adminAndUsers.append(db.usernamesInTheSite(username, x, "all"))

        return render_template('dashboard-3.html', pendingSites=pendingSites, currentDate=currentDate ,startD = startD, endD = endD, nbTotal=nbTotal, avgSpentm=avgSpentm,
                avgSpents = avgSpents,mostVistors=mostVistors, fewestVistors=fewestVistors,
                M_DAY = mostDays,F_DAY = fewestDays,currentSite=currentSite, addDate=addDate, username=username, userSites=userSites, user=user,
                 graph=graph, graphh=graphh, adminSite=adminSite, userSite=userSite, adminAndUsers=adminAndUsers, displayName=displayName)



    @app.route('/create-site', methods=['GET','POST'])
    def createSite():
        siteName = request.form['siteName']
        username = request.form['username']
        displayName =  db.displayname(username)
        currentSite = request.form['currentSite']
        currentSite = currentSite.lower()
        currentDate = request.form['currentDate']
        addDate  = date.today()
        startD = request.form['startD']
        endD = request.form['endD']
        nbTotal = request.form['nbTotal']
        avgSpentm = request.form['avgSpentm']
        avgSpents = request.form['avgSpents']
        mostVistors = request.form['mostVistors']
        fewestVistors = request.form['fewestVistors']
        mostDays = request.form['M_DAY']
        fewestDays = request.form['F_DAY']
        userSites = db.UserSites(username, "all")
        print("ddd",userSites)
        user = request.form['user']
        graph = request.form['graph']
        graphh = request.form['graphh']

        pendingSites = db.UserPendingSites(username)

        checkCreateStie = db.addToSite(username, siteName)

        adminSite = db.UserSites(username, "Admin")
        userSite = db.UserSites(username, "User")



        adminAndUsers = []
        for x in adminSite:
            adminAndUsers.append(db.usernamesInTheSite(username, x, "all"))

        


        return render_template('dashboard-3.html', pendingSites=pendingSites, currentDate=currentDate ,startD = startD, endD = endD, nbTotal=nbTotal, avgSpentm=avgSpentm,
                avgSpents = avgSpents,mostVistors=mostVistors, fewestVistors=fewestVistors,
                M_DAY = mostDays,F_DAY = fewestDays,currentSite=currentSite, addDate=addDate, username=username, userSites=userSites, user=user,
                 graph=graph, graphh=graphh, adminSite=adminSite, userSite=userSite, adminAndUsers=adminAndUsers,checkCreateStie=checkCreateStie, displayName=displayName)





    @app.route('/admin-sites', methods=['GET','POST'])
    def admin_sites():
        username = request.form['username']
        displayName =  db.displayname(username)
        adminSiteBeforeUpdate = request.form['adminSiteBeforeUpdate']
        selectedAdmin = request.form['selectedAdmin']
        selectedUser = request.form['selectedUser']
        currentSite = request.form['currentSite']
        currentSite = currentSite.lower()
        currentDate = request.form['currentDate']
        addDate  = date.today()
        startD = request.form['startD']
        endD = request.form['endD']
        nbTotal = request.form['nbTotal']
        avgSpentm = request.form['avgSpentm']
        avgSpents = request.form['avgSpents']
        mostVistors = request.form['mostVistors']
        fewestVistors = request.form['fewestVistors']
        mostDays = request.form['M_DAY']
        fewestDays = request.form['F_DAY']
        userSites = request.form['userSites']
        user = request.form['user']
        graph = request.form['graph']
        graphh = request.form['graphh']

        checkSiteName = None
       
        if selectedAdmin != "":
            senderEmail = db.inviteUserToSite(selectedAdmin, adminSiteBeforeUpdate, "Admin", username)
            if senderEmail != 0 :
                send_Invite(selectedAdmin, senderEmail)
                print()
        elif selectedUser != "":
            senderEmail = db.inviteUserToSite(selectedUser, adminSiteBeforeUpdate, "User", username)
            if senderEmail != 0 :
                send_Invite(selectedUser, senderEmail)
                print()
        delPermissionValue = request.form['delPermissionValue']
        print("Inviteeeee User",delPermissionValue, adminSiteBeforeUpdate)
        if delPermissionValue != "" and delPermissionValue:
            db.removeSiteFromUser(delPermissionValue, adminSiteBeforeUpdate)

        adminUpdatedSite = request.form['adminUpdatedSite']
        if adminUpdatedSite != "":
            checkSiteName = db.UpdateSiteName(adminSiteBeforeUpdate, adminUpdatedSite)
            
        exitAdminSite = request.form['exitAdminSite']
        if exitAdminSite != "":
            db.removeSiteFromUser(username, exitAdminSite)

        deletedSite = request.form['deletedSite']
        if deletedSite != "":
            db.removeSite(deletedSite)

        adminSite = db.UserSites(username, "Admin")
        userSite = db.UserSites(username, "User")
        adminAndUsers = []

      
        for x in adminSite:
            adminAndUsers.append(db.usernamesInTheSite(username ,x, "all"))

        pendingSites = db.UserPendingSites(username)


        return render_template('dashboard-3.html', pendingSites=pendingSites, currentDate=currentDate ,startD = startD, endD = endD, nbTotal=nbTotal, avgSpentm=avgSpentm,
                avgSpents = avgSpents,mostVistors=mostVistors, fewestVistors=fewestVistors,
                M_DAY = mostDays,F_DAY = fewestDays,currentSite=currentSite, addDate=addDate, username=username, userSites=userSites, user=user,
                 graph=graph, graphh=graphh, adminSite=adminSite, userSite=userSite, adminAndUsers=adminAndUsers, checkSiteName=checkSiteName, displayName=displayName)



    @app.route('/user_sites', methods=['GET','POST'])
    def user_sites():
        username = request.form['username']
        displayName =  db.displayname(username)
        currentSite = request.form['currentSite']
        currentSite = currentSite.lower()
        currentDate = request.form['currentDate']
        addDate  = date.today()
        startD = request.form['startD']
        endD = request.form['endD']
        nbTotal = request.form['nbTotal']
        avgSpentm = request.form['avgSpentm']
        avgSpents = request.form['avgSpents']
        mostVistors = request.form['mostVistors']
        fewestVistors = request.form['fewestVistors']
        mostDays = request.form['M_DAY']
        fewestDays = request.form['F_DAY']
        userSites = request.form['userSites']
        user = request.form['user']
        graph = request.form['graph']
        graphh = request.form['graphh']

       
        userSiteBeforeUpdate = request.form['userSiteBeforeUpdate']
        if userSiteBeforeUpdate != "":
            db.removeSiteFromUser(username, userSiteBeforeUpdate)
        


        adminSite = db.UserSites(username, "Admin")
        userSite = db.UserSites(username, "User")

        adminAndUsers = []
        for x in adminSite:
            adminAndUsers.append(db.usernamesInTheSite(username, x, "all"))

        pendingSites = db.UserPendingSites(username)

        return render_template('dashboard-3.html', pendingSites=pendingSites, currentDate=currentDate ,startD = startD, endD = endD, nbTotal=nbTotal, avgSpentm=avgSpentm,
                avgSpents = avgSpents,mostVistors=mostVistors, fewestVistors=fewestVistors,
                M_DAY = mostDays,F_DAY = fewestDays,currentSite=currentSite, addDate=addDate, username=username, userSites=userSites, user=user,
                 graph=graph, graphh=graphh, adminSite=adminSite, userSite=userSite, adminAndUsers=adminAndUsers, displayName=displayName)

        




    @app.route('/invited-sites', methods=['GET','POST'])
    def invited_sites():
        username = request.form['username']
        displayName =  db.displayname(username)
        currentSite = request.form['currentSite']
        currentSite = currentSite.lower()
        currentDate = request.form['currentDate']
        addDate  = date.today()
        startD = request.form['startD']
        endD = request.form['endD']
        nbTotal = request.form['nbTotal']
        avgSpentm = request.form['avgSpentm']
        avgSpents = request.form['avgSpents']
        mostVistors = request.form['mostVistors']
        fewestVistors = request.form['fewestVistors']
        mostDays = request.form['M_DAY']
        fewestDays = request.form['F_DAY']
        userSites = request.form['userSites']
        user = request.form['user']
        graph = request.form['graph']
        graphh = request.form['graphh']

        acceptSite = request.form['acceptSite']
        if acceptSite != "":
            db.acceptSite(username, acceptSite)

        rejectSite = request.form['rejectSite']
        if rejectSite != "":
            db.removeSiteFromUser(username, rejectSite)


        pendingSites = db.UserPendingSites(username)


        adminSite = db.UserSites(username, "Admin")
        userSite = db.UserSites(username, "User")

        adminAndUsers = []
        for x in adminSite:
            adminAndUsers.append(db.usernamesInTheSite(username, x, "all"))

       
        return render_template('dashboard-3.html', pendingSites=pendingSites, currentDate=currentDate ,startD = startD, endD = endD, nbTotal=nbTotal, avgSpentm=avgSpentm,
                avgSpents = avgSpents,mostVistors=mostVistors, fewestVistors=fewestVistors,
                M_DAY = mostDays,F_DAY = fewestDays,currentSite=currentSite, addDate=addDate, username=username, userSites=userSites, user=user,
                 graph=graph, graphh=graphh, adminSite=adminSite, userSite=userSite, adminAndUsers=adminAndUsers, displayName=displayName)

        



    @app.route('/dashboard/profile', methods = ['GET', 'POST'])
    def profile():
        currentDateOrg  = date.today()
        currentDate = str(currentDateOrg.strftime("%A %d %b %Y"))
        username = request.form['username']
        email = db.getEmail(username)
        currentSitee = request.form['currentSite']
        currentSite = currentSitee.lower()
        user = request.form['user']
        verify = request.form['verify']
        code = ""
        updateFname = request.form['updateFname']
        updateLname = request.form['updateLname']
        updateUsername = request.form['updateUsername']
        if  db.UserChecker(username) == False :
            username = updateUsername
        updateEmail = request.form['updateEmail']
        updatePassword = request.form['updatePassword']

        updatedName = False
        updatedUsername = False
        updatedEmail = False
        updatedPassword = False
        
        if len(updateFname) != 0:
            if db.update_Displayname(username , updateFname+" "+updateLname):
                updatedName = "updated"
            else:
                updatedName = "no update"
        elif len(updateUsername) != 0:
            if db.UserChecker(updateUsername) == False:
                if db.updateUsername(username, updateUsername):
                    username = updateUsername
                    updatedUsername = "updated"
            else:
                updatedUsername = "no update"
                
        elif  len(updateEmail) != 0:
            if db.EmailChecker(updateEmail) == False:
                if db.updateEmail(username ,updateEmail):
                    updatedEmail = "updated"
            else:
                updatedEmail = "no update"
        elif len(updatePassword) != 0:
            updatedPassword = db.updatePassword(username,updatePassword)
            if updatedPassword == True:
                updatedPassword = "updated"
            else:
                updatedPassword = "no update"
        elif verify == "otp":
            if email != None:
                code = random.randint(1000,9999)
                send_code(email, code)
        addDate  = date.today()

        displayName =  db.displayname(username)


        defaultDate = db.defaultDate(username, currentSite)
        nbTotal = 0
        if defaultDate != None:
            startD = defaultDate[0]
            endD = defaultDate[1]
            nbTotal = db.totalNumberOfVistors(currentSite, username, startD, endD)
            avgSpent = db.AvgTimeSpent(currentSite, username, startD, endD)
            avgSpentm = int(avgSpent / 60)
            avgSpents = int(( (avgSpent / 60) - int(avgSpent / 60) ) * 100)
            if currentSitee != "All sites":
                mostVistors = currentSitee
                fewestVistors = currentSitee
            else:
                mostVistors = db.SiteWithMaxVistors(username, startD, endD)
                fewestVistors = db.SiteWithFewestVistors(username, startD, endD)
            mostDays = db.FiveMostDaysOfVistors(username, currentSite, startD, endD)
            fewestDays = db.FiveFewestDaysOfVistors(username, currentSite, startD, endD)
            mostDays, fewestDays = dateFormat(mostDays, fewestDays)
            graph, graphh = getGraphs(username, currentSite, startD, endD)
        else:
            startD = addDate
            endD = addDate
            avgSpent = 0
            avgSpentm = 0
            avgSpents = 0
            mostVistors = 0
            fewestVistors = 0
            mostDays = 0
            fewestDays = 0
            mostDays, fewestDays = 0, 0
            graph, graphh = 0,0
        userSites = db.UserSites(username, "all")
        if userSites == [] or userSites == None:
            userSites = ""
            currentSite = "all sites"
            
        print(nbTotal)    

        if nbTotal == None :
            nbTotal = 0



        adminSite = db.UserSites(username, "Admin")
        userSite =  db.UserSites(username, "User")
        
        pendingSites = db.UserPendingSites(username)

        displayName =  db.displayname(username)
        siteNames, images = db.displayHeatMap(username, currentSite, startD, endD)

        adminAndUsers = []
        for x in adminSite:
            adminAndUsers.append(db.usernamesInTheSite(username, x, "all"))

        print(username)
        return render_template('dashboard.html', pendingSites=pendingSites, currentDate=currentDate ,startD = startD, endD = endD, nbTotal=nbTotal, avgSpentm=avgSpentm,
                avgSpents = avgSpents,mostVistors=mostVistors, fewestVistors=fewestVistors,
                M_DAY = mostDays,F_DAY = fewestDays,currentSite=currentSite, addDate=addDate, username=username, userSites=userSites, user=user,
                 graph=graph, graphh=graphh, adminSite=adminSite, userSite=userSite, adminAndUsers=adminAndUsers, siteNames=siteNames, images=images,
                 displayName=displayName, updatedName=updatedName, updatedUsername=updatedUsername, updatedEmail=updatedEmail, updatedPassword=updatedPassword, verify=verify, code=code, email=email)
                
    

    @app.route('/video-management/profile', methods = ['GET', 'POST'])
    def edit_profile():
        currentDateOrg  = date.today()
        currentDate = str(currentDateOrg.strftime("%A %d %b %Y"))
        username = request.form['username']
        email = db.getEmail(username)
        currentSite = request.form['currentSite']
        currentSite = currentSite.lower()
        user = request.form['user']
        verify = request.form['verify']
        code = ""
        updateFname = request.form['updateFname']
        updateLname = request.form['updateLname']
        updateUsername = request.form['updateUsername']
        if  db.UserChecker(username) == False :
            username = updateUsername
        updateEmail = request.form['updateEmail']
        updatePassword = request.form['updatePassword']

        updatedName = False
        updatedUsername = False
        updatedEmail = False
        updatedPassword = False
        
        if len(updateFname) != 0:
            if db.update_Displayname(username , updateFname+" "+updateLname):
                updatedName = "updated"
            else:
                updatedName = "no update"
        elif len(updateUsername) != 0:
            if db.UserChecker(updateUsername) == False:
                if db.updateUsername(username, updateUsername):
                    username = updateUsername
                    updatedUsername = "updated"
            else:
                updatedUsername = "no update"
                
        elif  len(updateEmail) != 0:
            if db.EmailChecker(updateEmail) == False:
                if db.updateEmail(username ,updateEmail):
                    updatedEmail = "updated"
            else:
                updatedEmail = "no update"
        elif len(updatePassword) != 0:
            updatedPassword = db.updatePassword(username,updatePassword)
            if updatedPassword == True:
                updatedPassword = "updated"
            else:
                updatedPassword = "no update"
        elif verify == "otp":
            if email != None:
                code = random.randint(1000,9999)
                send_code(email, code)
        addDate  = date.today()

        displayName =  db.displayname(username)
    
        siteName, videoAndDate = db.VideoName_with_siteName_List(username)

        userSites = db.UserSites(username, "all")
        if userSites == [] or userSites == None:
            userSites = ""
            currentSite = "all sites"

        displayName =  db.displayname(username)

        return render_template('dashboard-2.html', currentDate=currentDate ,currentSite=currentSite, addDate=addDate, username=username, userSites=userSites,
                 user=user,siteName=siteName, videoAndDate=videoAndDate, displayName=displayName,
                 updatedName=updatedName, updatedUsername=updatedUsername, updatedEmail=updatedEmail, updatedPassword=updatedPassword, verify=verify, code=code, email=email)


    

    @app.route('/site-management/profile', methods = ['GET', 'POST'])
    def update_profile():
        currentDateOrg  = date.today()
        currentDate = str(currentDateOrg.strftime("%A %d %b %Y"))
        username = request.form['username']
        email = db.getEmail(username)
        currentSite = request.form['currentSite']
        currentSite = currentSite.lower()
        user = request.form['user']
        verify = request.form['verify']
        code = ""
        updateFname = request.form['updateFname']
        updateLname = request.form['updateLname']
        updateUsername = request.form['updateUsername']
        if  db.UserChecker(username) == False :
            username = updateUsername
        updateEmail = request.form['updateEmail']
        updatePassword = request.form['updatePassword']

        updatedName = False
        updatedUsername = False
        updatedEmail = False
        updatedPassword = False
        
        if len(updateFname) != 0:
            if db.update_Displayname(username , updateFname+" "+updateLname):
                updatedName = "updated"
            else:
                updatedName = "no update"
        elif len(updateUsername) != 0:
            if db.UserChecker(updateUsername) == False:
                if db.updateUsername(username, updateUsername):
                    username = updateUsername
                    updatedUsername = "updated"
            else:
                updatedUsername = "no update"
                
        elif  len(updateEmail) != 0:
            if db.EmailChecker(updateEmail) == False:
                if db.updateEmail(username ,updateEmail):
                    updatedEmail = "updated"
            else:
                updatedEmail = "no update"
        elif len(updatePassword) != 0:
            updatedPassword = db.updatePassword(username,updatePassword)
            if updatedPassword == True:
                updatedPassword = "updated"
            else:
                updatedPassword = "no update"
        elif verify == "otp":
            if email != None:
                code = random.randint(1000,9999)
                send_code(email, code)
        addDate  = date.today()

        displayName =  db.displayname(username)
    


        userSites = db.UserSites(username, "all")
        if userSites == [] or userSites == None:
            userSites = ""
            currentSite = "all sites"

        displayName =  db.displayname(username)

        adminSite = db.UserSites(username, "Admin")
        userSite =  db.UserSites(username, "User")
        
        pendingSites = db.UserPendingSites(username)



        adminAndUsers = []
        for x in adminSite:
            adminAndUsers.append(db.usernamesInTheSite(username, x, "all"))

        displayName =  db.displayname(username)

        return render_template('dashboard-3.html',  pendingSites=pendingSites, currentDate=currentDate ,currentSite=currentSite, 
        addDate=addDate, username=username, userSites=userSites, user=user, adminSite=adminSite, userSite=userSite, 
        adminAndUsers=adminAndUsers, displayName=displayName, updatedName=updatedName, updatedUsername=updatedUsername,
        updatedEmail=updatedEmail, updatedPassword=updatedPassword, verify=verify, code=code, email=email)
      


    @app.errorhandler(NotFound)
    def handle_not_found(e):
        return render_template('error/404.html', title="404 Not Found")


    @app.errorhandler(InternalServerError)
    def handle_internal_server_error(e):
        return render_template('error/500.html', title='500 Internal Server Error')


    @app.errorhandler(MethodNotAllowed)
    def method_not_allowed(e):
        return render_template('error/405.html', title="405 Method Not Allowed")

    @app.errorhandler(BadRequest)
    def method_not_allowed(e):
        return render_template('error/405.html', title="400 Method Not Allowed")



    ## ================================================================================================= ##


    def send_Invite(receiver, sender):
        
        message = MIMEMultipart('alternative')

        #with open('./templates/invitation.html', 'r') as f:
         #   html = f.read()

        html = open("./templates/invitation.html").read().format(sender=sender)
        FROM = "analysight@hotmail.com"
        TO = receiver
        message["SUBJECT"] = "Invitation"    

        msg = MIMEText(html, 'html')
        message.attach(msg)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("analysight@gmail.com", "its4guys")
        server.sendmail(FROM, TO, message.as_string())
        server.quit()



    def send_code(receiver, code):
        
        message = MIMEMultipart('alternative')

        #with open('./templates/invitation.html', 'r') as f:
         #   html = f.read()

        html = open("./templates/code.html").read().format(code=code)
        FROM = "analysight_team@outlook.com"
        TO = receiver
        message["SUBJECT"] = "Invitation"    

        msg = MIMEText(html, 'html')
        message.attach(msg)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("analysight@gmail.com", "its4guys")
        server.sendmail(FROM, TO, message.as_string())
        print("eamil is send !")
        server.quit()    





    def dateFormat(mostDays, fewestDays):
        most = []
        fewest = []

        for x in range(len(mostDays)):
            most.append(str(mostDays[x].strftime("%a %d %b %Y")))

        for x in range(len(fewestDays)):
            fewest.append(str(fewestDays[x].strftime("%a %d %b %Y")))    

        return most, fewest



        
    def getSites(userSites):
        sites = []
        str = ''
        
        for x in range(len(userSites)):
            if userSites[x] != '\'' and userSites[x] != '[':
                if userSites[x] == ',' or userSites[x] == ']':
                    sites.append(str)
                    str = ''
                else:
                    if userSites[x] == " ":
                        if userSites[x-1] == "\'" or userSites[x-1] == " " or userSites[x+1] == "]":
                                k=0
                        else:
                            str = str + userSites[x]
                    else:
                        str = str + userSites[x]


        return sites



    def getGraph(data):
        days = ['Sunday', 'Monday', 'Thuesday', 'Wenesday', 'Thursday', 'Friday', 'Saturday']
        colors = {"Sunday": "#0C3B5D","Monday": "#3EC1CD","Thuesday": "#EF3A4C",
        "Wenesday": "#FCB94D", "Thursday": "#ed64bd", "Friday": "#69dbae",  "Saturday": "#8082ff"}

        fig = px.bar(x=days, y=data, color=days,  labels=dict(x="Days", y="", color="Day"), color_discrete_map=colors)
        return fig


    def getGraphs(username, siteName, startD, endD):


        days = ['Sunday', 'Monday', 'Thuesday', 'Wenesday', 'Thursday', 'Friday', 'Saturday']
        months = ["January","February","March","April","May","June","July", "August","September","October","November","December"]

        dayColors = {"Sunday": "#0C3B5D","Monday": "#3EC1CD","Thuesday": "#EF3A4C",
        "Wenesday": "#FCB94D", "Thursday": "#ed64bd", "Friday": "#69dbae",  "Saturday": "#8082ff"}

        monthColors = {"January": "#0C3B5D","February": "#3EC1CD","March": "#EF3A4C",
        "April": "#FCB94D", "May": "#ed64bd", "June": "#69dbae",  "July": "#8082ff", "August":"#d99b7c",
        "September" : "#8bc4c3", "October" : "#96cbff", "November" : "#ff9698", "December" : "#8695bf"}

                   
        avgDays = db.AvgVistorsPerDay(username , siteName , startD , endD)

        avgMonths = db.AvgVistorsPerMonth(username , siteName , startD , endD)



        df = pd.DataFrame({'Day': days,'Average': avgDays})
        fig = px.bar(df, x='Day', y='Average', color="Day",labels=dict(x="Days", y="", color="Day"), color_discrete_map=dayColors)
        graph = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        dff = pd.DataFrame({'Month': months,'Average': avgMonths})
        figg = px.bar(dff, x='Month', y='Average', color="Month",labels=dict(x="Months", y="", color="Month"), color_discrete_map=monthColors)
        graphh = json.dumps(figg, cls=plotly.utils.PlotlyJSONEncoder)  

        return   graph, graphh


    return app
    
app = create_app()	
    
if __name__=="__main__":

    app.run(debug=True, host="0.0.0.0", port="80")

