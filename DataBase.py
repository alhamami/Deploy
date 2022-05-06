#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#


from datetime import datetime
from flask import Flask


from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import  func, Column, String, create_engine
import json
import os
import bcrypt

'''
from datetime import datetime
from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import asc , func
'''



#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


db = SQLAlchemy()
''''''

database_path = 'postgresql://postgres:o0kARjWrSUxAcv61DyEM@containers-us-west-50.railway.app:5714/railway'

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''

def setup_db(app,database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


'''
app = Flask(__name__)
moment = Moment(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:112233@localhost:5432/Analysight'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
'''
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class User(db.Model):
    __tablename__ = 'User'

    userId = db.Column(db.Integer, primary_key=True , autoincrement=True)
    name = db.Column(db.String, nullable=True)
    display_name = db.Column(db.String, nullable=True)
    emailAddress = db.Column(db.String(120), nullable=True)
    password = db.Column(db.LargeBinary, nullable=True)

    UserAndSite = db.relationship('UserAndSite', backref='User' , passive_deletes=True , lazy=True)

class Site(db.Model):
    __tablename__ = 'Site'

    siteId = db.Column(db.Integer, primary_key=True , autoincrement=True)
    siteName = db.Column(db.String, nullable=False)

    UserAndSite = db.relationship('UserAndSite', backref='Site', passive_deletes=True , lazy=True)

class UserAndSite(db.Model):
    __tablename__ = 'UserAndSite'

    UserAndSite_id = db.Column(db.Integer, primary_key=True , autoincrement=True)
    User_id = db.Column(db.Integer, db.ForeignKey('User.userId' , ondelete='CASCADE'), nullable=False)
    Site_id = db.Column(db.Integer, db.ForeignKey('Site.siteId' , ondelete='CASCADE'), nullable=False)
    Role = db.Column(db.String, nullable=False)
    State = db.Column(db.String , nullable=False)

class Video(db.Model):
    __tablename__ = 'Video'

    video_id = db.Column(db.Integer, primary_key=True , autoincrement=True)
    site_id = db.Column(db.Integer, db.ForeignKey('Site.siteId' , ondelete='CASCADE'), nullable=False)
    number_of_vistors = db.Column(db.Integer, nullable=False)
    time_spent =db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    day = db.Column(db.String, nullable=False)
    month = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=False)
    video_name = db.Column(db.String , nullable=False)



#----------------------------------------------------------------------------#
#                               Query section.                               #
#----------------------------------------------------------------------------#

def totalNumberOfVistors(siteName , username , start_date , end_date):

    if (siteName != 'all sites'):
        qry = db.session.query(func.sum(Video.number_of_vistors)).filter(func.lower(User.name) == func.lower(username) , UserAndSite.User_id == User.userId ,
        func.lower(Site.siteName) == func.lower(siteName)  , UserAndSite.Site_id == Site.siteId , Video.site_id == UserAndSite.Site_id , UserAndSite.State != 'Pending' ,
        Video.date.between(start_date , end_date)).all()

    else :
        qry = db.session.query(func.sum(Video.number_of_vistors)).filter(func.lower(User.name) == func.lower(username)  , UserAndSite.User_id == User.userId ,
        UserAndSite.Site_id == Site.siteId , Video.site_id == UserAndSite.Site_id , UserAndSite.State != 'Pending',
        Video.date.between(start_date , end_date)).all()

    print(qry[0][0])
    return qry[0][0]

    
def AvgTimeSpent(siteName , username , start_date , end_date):

    if (siteName != 'all sites'):
        qry = db.session.query(func.sum(Video.time_spent)).filter(func.lower(User.name) == func.lower(username)  , UserAndSite.User_id == User.userId ,
        func.lower(Site.siteName) == func.lower(siteName)  , UserAndSite.Site_id == Site.siteId , Video.site_id == UserAndSite.Site_id , UserAndSite.State != 'Pending' ,
        Video.date.between(start_date , end_date)).group_by(Video.date).all()
       

    else :
        qry = db.session.query(func.sum(Video.time_spent)).filter(func.lower(User.name) == func.lower(username)  , UserAndSite.User_id == User.userId ,
        UserAndSite.Site_id == Site.siteId , Video.site_id == UserAndSite.Site_id , UserAndSite.State != 'Pending' ,
        Video.date.between(start_date , end_date)).group_by(Video.date).all()
    sum = 0
    if qry is None:
        return None
    else:
        for i in range(len(qry)):
            sum = sum + qry[i][0]
        if len(qry) == 0:
            avg = 0
        else:
          avg = sum/len(qry)
        print(avg)
        return avg


def SiteWithMaxVistors(username , start_date , end_date):

    qry = db.session.query(func.sum(Video.number_of_vistors) , Video.site_id).filter(func.lower(User.name) == func.lower(username)  , UserAndSite.User_id == User.userId,
    UserAndSite.Site_id == Site.siteId , Video.site_id == UserAndSite.Site_id , UserAndSite.State != 'Pending' ,
     Video.date.between(start_date , end_date)).group_by(Video.site_id).all()
    qry.sort(reverse=True)
    qry2 = db.session.query(Site.siteName).filter(Site.siteId == qry[0][1]).all()
    print(qry2[0][0])


    return qry2[0][0]


def SiteWithFewestVistors(username , start_date , end_date):

    qry = db.session.query(func.sum(Video.number_of_vistors) , Video.site_id).filter(func.lower(User.name) == func.lower(username)  , UserAndSite.User_id == User.userId,
    UserAndSite.Site_id == Site.siteId , Video.site_id == UserAndSite.Site_id , UserAndSite.State != 'Pending' ,
     Video.date.between(start_date , end_date)).group_by(Video.site_id).all()
    qry.sort(reverse=False)
    qry2 = db.session.query(Site.siteName).filter(Site.siteId == qry[0][1]).all()
    print(qry2[0][0])


    return qry2[0][0]


def FiveMostDaysOfVistors(username , siteName , start_date , end_date):

    if (siteName != 'all sites'): 

        qry = db.session.query(func.sum(Video.number_of_vistors) , Video.date).filter(func.lower(User.name) == func.lower(username)  , UserAndSite.User_id == User.userId ,
        UserAndSite.Site_id == Video.site_id , UserAndSite.Site_id == Site.siteId , func.lower(Site.siteName) == func.lower(siteName)  ,
        Video.site_id == UserAndSite.Site_id , UserAndSite.State != 'Pending' ,
         Video.date.between(start_date , end_date)).group_by(Video.date).all()
    else :
        qry = db.session.query(func.sum(Video.number_of_vistors) , Video.date).filter(func.lower(User.name) == func.lower(username)  , UserAndSite.User_id == User.userId ,
        UserAndSite.Site_id == Video.site_id , UserAndSite.State != 'Pending' , 
        Video.date.between(start_date , end_date)).group_by(Video.date).all()

    qry.sort(reverse=True)
    list = []
    count = 0
    for i in range(len(qry)):
        if (count >= 5 or len(qry) == 0):
            break
        list.append(qry[i][1])
        count = count+1

    print(list)
    return list

def FiveFewestDaysOfVistors(username , siteName , start_date , end_date):


    if (siteName != 'all sites'): 

        qry = db.session.query(func.sum(Video.number_of_vistors) , Video.date).filter(func.lower(User.name) == func.lower(username)  , UserAndSite.User_id == User.userId ,
        UserAndSite.Site_id == Video.site_id , UserAndSite.Site_id == Site.siteId , func.lower(Site.siteName) == func.lower(siteName)  ,
        Video.site_id == UserAndSite.Site_id , UserAndSite.State != 'Pending' ,
         Video.date.between(start_date , end_date)).group_by(Video.date).all()
    else :
        qry = db.session.query(func.sum(Video.number_of_vistors) , Video.date).filter(func.lower(User.name) == func.lower(username)  , UserAndSite.User_id == User.userId ,
        UserAndSite.Site_id == Video.site_id , UserAndSite.State != 'Pending' , 
        Video.date.between(start_date , end_date)).group_by(Video.date).all()

    qry.sort(reverse=False)
    list = []
    count = 0
    for i in range(len(qry)):
        if (count >= 5 or len(qry) == 0):
            break
        list.append(qry[i][1])
        count = count+1

    print(list)
    return list

def AvgVistorsPerDay(username , siteName , start_date , end_date):

    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    result = []

    if (siteName != 'all sites'):
        for day in days:
            value1 = db.session.query(func.sum(Video.number_of_vistors)).filter(func.lower(User.name) == func.lower(username)  , UserAndSite.User_id == User.userId ,
                UserAndSite.Site_id == Site.siteId , func.lower(Site.siteName) == func.lower(siteName)  , Video.site_id == UserAndSite.Site_id , UserAndSite.State != 'Pending' , 
                Video.date.between(start_date , end_date) ,  Video.day == day).all()[0][0]
                
            value2 = db.session.query(func.sum(Video.number_of_vistors)).filter(func.lower(User.name) == func.lower(username)  , UserAndSite.User_id == User.userId ,
                UserAndSite.Site_id == Site.siteId , func.lower(Site.siteName) == func.lower(siteName)  , Video.site_id == UserAndSite.Site_id , UserAndSite.State != 'Pending' ,
                Video.date.between(start_date , end_date) ,  Video.day == day).group_by(Video.date).all()
                
            if value1 is None or  len(value2) == 0:
                res = 0
            else:
                res = value1 / len(value2)

            result.append(res)
    else :
            for day in days:
                value1 = db.session.query(func.sum(Video.number_of_vistors)).filter(func.lower(User.name) == func.lower(username)  , UserAndSite.User_id == User.userId ,
                    UserAndSite.Site_id == Site.siteId , Video.site_id == UserAndSite.Site_id , UserAndSite.State != 'Pending' ,
                    Video.date.between(start_date , end_date) ,  Video.day == day).all()[0][0]
                
                value2 = db.session.query(func.sum(Video.number_of_vistors)).filter(func.lower(User.name) == func.lower(username)  , UserAndSite.User_id == User.userId ,
                    UserAndSite.Site_id == Site.siteId , Video.site_id == UserAndSite.Site_id , UserAndSite.State != 'Pending' ,
                    Video.date.between(start_date , end_date) ,  Video.day == day).group_by(Video.date).all()
                
                if value1 is None or  len(value2) == 0:
                    res = 0
                else:
                    res = value1 / len(value2)

                result.append(res)

    print(result)
    return result

def AvgVistorsPerMonth(username , siteName , start_date , end_date):

    months = ["January","February","March","April","May","June","July", "August","September","October","November","December"]
    result = []

    if (siteName != 'all sites'):
        for month in months:
            value1 = db.session.query(func.sum(Video.number_of_vistors)).filter(func.lower(User.name) == func.lower(username)  , UserAndSite.User_id == User.userId ,
                UserAndSite.Site_id == Site.siteId , func.lower(Site.siteName) == func.lower(siteName)  , Video.site_id == UserAndSite.Site_id , UserAndSite.State != 'Pending' , 
                Video.date.between(start_date , end_date) ,  Video.month == month).all()[0][0]
                
            value2 = db.session.query(func.sum(Video.number_of_vistors)).filter(func.lower(User.name) == func.lower(username)  , UserAndSite.User_id == User.userId ,
                UserAndSite.Site_id == Site.siteId , func.lower(Site.siteName) == func.lower(siteName)  , Video.site_id == UserAndSite.Site_id , UserAndSite.State != 'Pending' ,
                Video.date.between(start_date , end_date) ,  Video.month == month).group_by(Video.date).all()
                
            if value1 is None or  len(value2) == 0:
                res = 0
            else:
                res = value1 / len(value2)

            result.append(res)
    else :
            for month in months:
                value1 = db.session.query(func.sum(Video.number_of_vistors)).filter(func.lower(User.name) == func.lower(username)  , UserAndSite.User_id == User.userId ,
                    UserAndSite.Site_id == Site.siteId , Video.site_id == UserAndSite.Site_id , UserAndSite.State != 'Pending' ,
                    Video.date.between(start_date , end_date) ,  Video.month == month).all()[0][0]
                
                value2 = db.session.query(func.sum(Video.number_of_vistors)).filter(func.lower(User.name) == func.lower(username)  , UserAndSite.User_id == User.userId ,
                    UserAndSite.Site_id == Site.siteId , Video.site_id == UserAndSite.Site_id , UserAndSite.State != 'Pending' ,
                    Video.date.between(start_date , end_date) ,  Video.month == month).group_by(Video.date).all()
                
                if value1 is None or  len(value2) == 0:
                    res = 0
                else:
                    res = value1 / len(value2)

                result.append(res)

    print(result)
    return result
  
    

def LoginChecker(username , password):
    
    if username != None:
        username = username.strip()

    qry = db.session.query(User.name , User.password).filter(func.lower(User.name) == func.lower(username)).all()
    if qry is None or len(qry) == 0:
        print('wrong username!')
        return False
    elif bcrypt.checkpw(password.encode('utf-8'), qry[0][1]):
        print('true!')
        return True
    else:
        print('wrong password!')
        return False

def UserSites(username , Role):
    list = []
    if (Role == 'all'):
        qry = db.session.query(Site.siteName).filter(func.lower(User.name) == func.lower(username)  , UserAndSite.User_id == User.userId ,
        UserAndSite.State != 'Pending' , UserAndSite.Site_id == Site.siteId).all()
    else:
        qry = db.session.query(Site.siteName).filter(func.lower(User.name) == func.lower(username)  , UserAndSite.User_id == User.userId ,
        UserAndSite.Site_id == Site.siteId , UserAndSite.State != 'Pending' , UserAndSite.Role == Role).all()

    for i in range(len(qry)):
        list.append(qry[i][0])

    print(list)

    return list

def usernamesInTheSite(username, siteName , Role):
    res = []
    if Role == 'all':
        qry = db.session.query(User.name).filter(func.lower(Site.siteName) == func.lower(siteName)  , func.lower(User.name) != func.lower(username) , UserAndSite.Site_id == Site.siteId ,
        User.userId == UserAndSite.User_id , UserAndSite.State != 'Pending').all()

        qry2 = db.session.query(User.emailAddress).filter(func.lower(Site.siteName) == func.lower(siteName)  , func.lower(User.name) != func.lower(username), UserAndSite.Site_id == Site.siteId ,
        User.userId == UserAndSite.User_id , UserAndSite.State == 'Pending').all()

        qry3 = db.session.query(User.emailAddress).filter(User.name == None , func.lower(Site.siteName) == func.lower(siteName)  , UserAndSite.Site_id == Site.siteId ,
        User.userId == UserAndSite.User_id , UserAndSite.State == 'Pending').all()

        qry4 = db.session.query(User.display_name).filter(func.lower(Site.siteName) == func.lower(siteName)  , func.lower(User.name) != func.lower(username) , UserAndSite.Site_id == Site.siteId ,
        User.userId == UserAndSite.User_id , UserAndSite.State != 'Pending').all()

    else:
        qry = db.session.query(User.name).filter(func.lower(Site.siteName) == func.lower(siteName)  , func.lower(User.name) != func.lower(username), UserAndSite.Site_id == Site.siteId ,
        User.userId == UserAndSite.User_id , UserAndSite.State != 'Pending',  UserAndSite.Role == Role).all()

        qry2 = db.session.query(User.emailAddress).filter(func.lower(Site.siteName) == func.lower(siteName)  , func.lower(User.name) != func.lower(username), UserAndSite.Site_id == Site.siteId ,
        User.userId == UserAndSite.User_id , UserAndSite.State == 'Pending',  UserAndSite.Role == Role).all()

        qry3 = db.session.query(User.emailAddress).filter(User.name == None , func.lower(Site.siteName) == func.lower(siteName)  , UserAndSite.Site_id == Site.siteId ,
        User.userId == UserAndSite.User_id , UserAndSite.State == 'Pending' , UserAndSite.Role == Role).all()

        qry4 = db.session.query(User.display_name).filter(func.lower(Site.siteName) == func.lower(siteName)  , func.lower(User.name) != func.lower(username) , UserAndSite.Site_id == Site.siteId ,
        User.userId == UserAndSite.User_id , UserAndSite.State != 'Pending').all()
    
    if len(qry) !=0:
        for i in range(len(qry)):
            res.append(qry4[i][0] + " (" + qry[i][0] + ")")
    if len(qry2) !=0:
        for i in range(len(qry2)):
            res.append(str(qry2[i][0])+" | invited")

    if len(qry3) !=0:
        for i in range(len(qry3)):
            res.append(str(qry3[i][0])+" | invited")

    print(res)

    return res


def UserRelation(username):
    list = []
    qry = db.session.query(Site.siteName).filter(func.lower(User.name) == func.lower(username)  , UserAndSite.User_id == User.userId ,
    UserAndSite.Site_id == Site.siteId , UserAndSite.State != 'Pending' ).all()
    for i in range(len(qry)):
        qry2 = db.session.query(User.name).filter(Site.siteName == qry[i][0] , UserAndSite.Site_id == Site.siteId ,
         UserAndSite.User_id == User.userId).all()
        for x in range (len(set(qry2))):
            if str(qry2[x][0]) != username:
                list.append(str(qry2[x][0]))
    list = set(list)
    print(list)
    return list


def SiteWithoutResult(siteName):
    qry = db.session.query(Video.site_id).filter(func.lower(Site.siteName) == func.lower(siteName)  , Video.site_id == Site.siteId).all()
    if len(qry) == 0:
        print('the site with name ' + siteName + ' has no result!')
        return True
    else:
        print('the site with name ' + siteName + ' has result!')
        return False


def CheckRole(username , siteName):
    qry = db.session.query(UserAndSite.Role).filter(func.lower(User.name) == func.lower(username)  , func.lower(Site.siteName) == func.lower(siteName)  , UserAndSite.Site_id == Site.siteId ,
    UserAndSite.User_id == User.userId).all()

    if len(qry) == 0:
        print('The ' + username +' or ' + siteName +' not found!')
        return False
    
    print(qry[0][0])
    return qry[0][0]


def defaultDate(username , siteName):
    siteName = siteName.strip()
    username = username.strip()
    res = []
    if siteName == 'all sites':
        qry = db.session.query(func.min(Video.date) , func.max(Video.date)).filter(func.lower(User.name) == func.lower(username)  ,
        UserAndSite.User_id == User.userId , Video.site_id == UserAndSite.Site_id).all()
    else:
        print("rfrf")
        qry = db.session.query(func.min(Video.date) , func.max(Video.date)).filter(func.lower(User.name) == func.lower(username)  , 
        Site.siteName == siteName , UserAndSite.Site_id == Site.siteId,  UserAndSite.User_id == User.userId , Video.site_id == UserAndSite.Site_id).all()

    if qry[0][0] != None:
        res.append(qry[0][0].strftime("%Y-%m-%d"))
        res.append(qry[0][1].strftime("%Y-%m-%d"))
        print(res)
        return res
    
    return None


def UserPendingSites(username):
    qry = db.session.query(Site.siteName).filter(func.lower(User.name) == func.lower(username)  , UserAndSite.User_id == User.userId , 
    UserAndSite.State == 'Pending' , UserAndSite.Site_id == Site.siteId).all()
    res = []

    for i in range(len(qry)):
        res.append(qry[i][0])

    print(res)
    return res


def userWithoutRelation(siteName):
    qry = db.session.query(User.name).filter(func.lower(Site.siteName) == func.lower(siteName)  , UserAndSite.Site_id == Site.siteId ,
        User.userId == UserAndSite.User_id , UserAndSite.State != 'Pending').all()
    qry2 = db.session.query(User.name).all()
    
    res = []
    for i in qry2:
         if i not in qry:
             res.append(i)

    print(res)
    return res
    

def displayHeatMap(username , siteName , start_date , end_date):

    SiteNames = []
    SiteHeatMaps = []

    if siteName != 'all sites':
        qry1 = db.session.query(func.max(Video.number_of_vistors)).filter(func.lower(Site.siteName) == func.lower(siteName)  , Video.site_id == Site.siteId ,
          func.lower(User.name) == func.lower(username)  , UserAndSite.User_id == User.userId ,
        UserAndSite.Site_id ==Site.siteId, UserAndSite.State != 'Pending' , Video.date.between(start_date , end_date)).all()[0][0]
        if qry1 != None:
            qry2 = db.session.query(Video.image , Video.date).filter(Video.number_of_vistors == qry1 , func.lower(Site.siteName) == func.lower(siteName)  , Video.site_id == Site.siteId).all()

            SiteNames.append(str(siteName).title() +" With Most Visitors Day in "+str(qry2[0][1]))
            SiteHeatMaps.append(qry2[0][0])
            print(SiteNames)
            print ( SiteHeatMaps)


        return SiteNames , SiteHeatMaps

    else:
        check = db.session.query(func.max(Video.number_of_vistors)).all()
        if check[0][0] == None:

            print(SiteNames)
            print(SiteHeatMaps)
            return SiteNames , SiteHeatMaps

        usersites = UserSites(username , 'all')
        for i in usersites:
            qry1 = db.session.query(func.max(Video.number_of_vistors) , Site.siteName).filter(Site.siteName == i , Video.site_id == Site.siteId ,
            func.lower(User.name) == func.lower(username)  , UserAndSite.User_id == User.userId , UserAndSite.State != 'Pending' ,
            UserAndSite.Site_id ==Site.siteId, Video.date.between(start_date , end_date)).group_by(Site.siteName).all()

            if len(qry1) != 0:
                qry2 = db.session.query(Site.siteName , Video.image , Video.date).filter(Video.number_of_vistors == qry1[0][0] , Site.siteName == qry1[0][1]
                , Video.site_id == Site.siteId).all()
                
                qry2 = list(dict.fromkeys(qry2))
                SiteNames.append(str(qry2[0][0]).title() +" With Most Visitors Day in "+str(qry2[0][2]))
                SiteHeatMaps.append(qry2[0][1])

        print(SiteNames)
        print(SiteHeatMaps)
        return SiteNames , SiteHeatMaps
        

def EmailAndUserCheaker(usernme , email):
    if usernme != None and email != None:
        print('Empty username or email!')
        return False
    qry = db.session.query(User.userId).filter(func.lower(User.name) == func.lower(usernme) ,
     func.lower(User.emailAddress) == func.lower(email)).all()
    if len(qry) == 0:
        print('False')
        return False
    else:
        print('True')
        return True


def displayname(username):
    qry = db.session.query(User.display_name).filter(func.lower(User.name) == func.lower(username)).all()
    if len(qry) != 0:
        print("the display name for "+username+" is "+qry[0][0])
        return qry[0][0]
    else:
        print("there is no display name for "+username)
        return False


def checkUserSite(username):
    qry = db.session.query(Site.siteId).filter(func.lower(User.name) == func.lower(username)  , UserAndSite.User_id == User.userId).all()
    print(qry)
    return len(qry)

def inviteUserToSite(Email , siteName , Role, Sender):
    if Email == None:
        print("you can't enter empty email!")
        return False
    username = db.session.query(User.name).filter(User.emailAddress == Email).all()
    senderEmail = db.session.query(User.emailAddress).filter(User.name == Sender).all()
    print(username)
    if len(username) == 0:
        Email = Email.strip()
        print(Email)
        addToUser(None , None , Email , None)
        addToPermission(Email, siteName , Role , 'Pending')
        senderEmail = str(senderEmail)
        start = senderEmail.find('(') + 2
        end = senderEmail.find(')') - 2
        senderEmail = senderEmail[start:end]
        return str(senderEmail)

    else:
        addToPermission(username[0][0] , siteName , Role , 'Pending')
        return 0


def acceptSite(username , siteName):
    try:
        qry = db.session.query(UserAndSite).filter(func.lower(User.name) == func.lower(username)  , UserAndSite.User_id == User.userId ,
         func.lower(Site.siteName) == func.lower(siteName)  , UserAndSite.Site_id == Site.siteId ,
        UserAndSite.State == 'Pending')
        if (len(qry.all()) == 0):
            print('Erorr updating the state !')
            return False
        else:
            qry.update({UserAndSite.State : 'Active'} , synchronize_session='fetch')
            db.session.commit()
            db.session.close()
            print('the state has been changed successfully ')
            return True

    except Exception as e :
     
        db.session.rollback()
        print('Erorr accord while updating the state !' + str(e))
        return False

def VideoName_with_siteName_List(username):
    
    qry = db.session.query(Site.siteName , Video.video_id).filter(func.lower(User.name) == func.lower(username)  , UserAndSite.User_id == User.userId 
    , Video.site_id == UserAndSite.Site_id , UserAndSite.State != 'Pending' , Site.siteId == Video.site_id).all()
    
    if len(qry) == 0:
        print('there is an erorr!')
        return [], []
    else:
        dictionary = {}

        for a, b in qry:
            dictionary.setdefault(a, []).append(b)

        VideoLists = []
        SiteNames = []
        dateList = []
        temp = []
        SiteNames = list(dictionary.keys())
        
        for i in SiteNames:
            VideoLists.append(dictionary[i])
        
        for i in VideoLists:

            for k in i:
                temp.append(db.session.query(Video.date).filter(Video.video_id == k).all()[0][0])
                
            dateList.append(temp)
            temp =[]


        '''
        print()
        print(dictionary)
        print()
        print(SiteNames)
        print()
        print(VideoLists)
        print()
        print(dateList)
        print()
        '''
        videoAndDate = []
 
        for x in range(len(VideoLists)):
            lists = []
            for z in range(len(VideoLists[x])):
                video_name = db.session.query(Video.video_name).filter(Video.video_id == VideoLists[x][z]).all()
                lists.append(video_name[0][0] + '(' +str(VideoLists[x][z])+ ') | ' + dateList[x][z].strftime("%Y-%m-%d"))
            videoAndDate.append(lists)   
        print(videoAndDate)
        return SiteNames , videoAndDate
        



#----------------------------------------------------------------------------#
#                               insert section.                              #
#----------------------------------------------------------------------------#


def addToUser(name , display_name , emailAddress , password):
    prim_qry = db.session.query(func.max(User.userId)).all()
    if emailAddress != None:
        emailAddress = emailAddress.strip()
        emailAddress = emailAddress.lower()
    if name != None:
        name = name.strip()
        name = name.lower()
    if password != None:
        password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    if prim_qry is None:
        prim_qry = 0
    elif(prim_qry[0][0] == None):
        prim_qry = 0

    try:
        qry = db.session.query(User.name).filter(User.name == name).all()
        if len(qry) != 0:
            if qry[0][0] == None:
                qry = []
        checkEmail = db.session.query(User).filter(User.emailAddress == emailAddress)
        temp = db.session.query(User.name).filter(User.emailAddress == emailAddress)
        if(len(qry) == 0 and len(checkEmail.all()) == 0):
            if(type(prim_qry) is int):
                newUser = User(userId = prim_qry+1 , name = name , display_name = display_name , emailAddress = emailAddress , password = password)
            else:
                newUser = User(userId = prim_qry[0][0]+1 , name = name , display_name = display_name , emailAddress = emailAddress , password = password)
            db.session.add(newUser)
            db.session.commit()
            db.session.close()
            print("User added successfully")
            return True

        elif(temp.all()[0][0] == None and len(checkEmail.all()) == 1 and len(qry) == 0):

            checkEmail.update({User.name : name , User.display_name : display_name , User.password : password} , synchronize_session='fetch')
            db.session.commit()
            db.session.close()
            print('the information has been updated successfully to the email with name ' + emailAddress)
            return True
        else:
            print('Erorr!!')
            return False
    except:
        db.session.rollback()
        print("There is an error in adding the user")
        db.session.close()
        return False


def addToSite(username , siteName):
    if username == None or siteName == None:
        print('None username or None siteName')
        return False
    if siteName.isspace() or username.isspace():
        print('Empty username or Empty siteName')
        return False
    username = username.strip()
    siteName = siteName.strip()

    prim_qry1 = db.session.query(func.max(Site.siteId)).all()[0][0]
    prim_qry2 = db.session.query(func.max(UserAndSite.UserAndSite_id)).all()[0][0]
    qry1 = db.session.query(User.userId).filter(func.lower(User.name) == func.lower(username) ).all()
    check1 = db.session.query(Site.siteId).filter(func.lower(Site.siteName) == func.lower(siteName)).all()
    if len(check1) > 0:
        print('there are site with name : ' +siteName)
        return False
    if prim_qry1 is None:
        prim_qry1 = 0
    if prim_qry2 is None:
        prim_qry2 = 0
    try:
        newSite = Site(siteId = prim_qry1+1 , siteName = siteName )
        db.session.add(newSite)
        db.session.commit()
        qry2 = db.session.query(func.max(Site.siteId)).filter(func.lower(Site.siteName) == func.lower(siteName) ).all()
        check = db.session.query(UserAndSite.Site_id).filter(UserAndSite.User_id == qry1[0][0] , UserAndSite.Site_id == qry2[0][0]).all()
        if (len(check) == 0):
            newPer = UserAndSite(UserAndSite_id = prim_qry2 +1 ,User_id = qry1[0][0] , Site_id = qry2[0][0] , Role = 'Admin' , State = 'Active')
            db.session.add(newPer)
            db.session.commit()
            print("Site added successfully")
            db.session.close()
            return True
        else:
            print('Erorr , '+username+' already linked to ' + siteName)
            db.session.close()
            return False


    except:
        db.session.rollback()
        print("There is an error in adding the site")
        db.session.close()
        return False


def EmailChecker(email):
    qry = db.session.query(User.userId).filter(func.lower(User.emailAddress) == func.lower(email), User.name != None , User.password != None).all()
    if len(qry) == 0:
        print('False')
        return False
    else:
        print('True')
        return True


def getEmail(username):
    qry = db.session.query(User.emailAddress).filter(func.lower(User.name) == func.lower(username)).all()
    if len(qry) == 0:
          print('False: There is no email for '+username)
    else:
        print('True: There email of '+username+' is '+qry[0][0])
        return qry[0][0]


def UserChecker(username):
    qry = db.session.query(User.userId).filter(func.lower(User.name) == func.lower(username)).all()
    if len(qry) == 0:
        print('False: There is no user with same name '+username)
        return False
    else:
        print('True: There is user with same name '+username)
        return qry




def addToPermission(name_or_email , siteName , Role , state):
    prim_qry = db.session.query(func.max(UserAndSite.UserAndSite_id)).all()
    try:
        if name_or_email == None:
            qry1 = db.session.query(User.userId).filter(User.name == name_or_email).all()
        elif name_or_email.find('@') == -1:
            qry1 = db.session.query(User.userId).filter(User.name == name_or_email).all()
        else:
            qry1 = db.session.query(User.userId).filter(User.emailAddress == name_or_email).all()

        qry2 = db.session.query(Site.siteId).filter(func.lower(Site.siteName) == func.lower(siteName) ).all()
        check = db.session.query(UserAndSite.Site_id , UserAndSite.State).filter(UserAndSite.User_id == qry1[0][0]
         , UserAndSite.Site_id == qry2[0][0]).all()
        if(len(check) == 0):
            newTable = UserAndSite(UserAndSite_id = prim_qry[0][0]+1, User_id = qry1[0][0] , Site_id = qry2[0][0] , Role = Role ,
             State = state)
            db.session.add(newTable)
            db.session.commit()
            print("The user has been linked to the appropriate site!")
            db.session.close()
            return True
        else:
            if(check[0][1] == 'Pending'):
                print('Erorr , '+name_or_email+' already invited to ' + siteName)
            else:
                print('Erorr , '+name_or_email+' already linked to ' + siteName)
            return False
    except:
        db.session.rollback()
        print("There is a problem connecting the user to the right site")
        db.session.close()
        return False


def addToVideo(siteName , number_of_vistors , time_spent , date , image , Video_name):
    prim_qry = db.session.query(func.max(Video.video_id)).all()[0][0]
    if(prim_qry is None):
        prim_qry = 0
    try:
        check = db.session.query(func.lower(Site.siteName) == func.lower(siteName) ).all()
        if (len(check) == 0):
            print('Erorr : there are no site with name '+siteName)
            return False
        else:
            qry1 = db.session.query(Site.siteId).filter(func.lower(Site.siteName) == func.lower(siteName) ).all()
            newVideo = Video(video_id = prim_qry+1, site_id = qry1[0][0] , number_of_vistors = number_of_vistors ,
            time_spent = time_spent , date = date , day = datetime.strptime(date, "%Y-%m-%d").strftime("%A") , 
            month = datetime.strptime(date, "%Y-%m-%d").strftime("%B") , image = image , video_name = Video_name)

            db.session.add(newVideo)
            db.session.commit()
            print("Video added successfully")
            db.session.close()
            return True
    except:
        db.session.rollback()
        print("There is an error in adding the video")
        db.session.close()
        return False



#----------------------------------------------------------------------------#
#                               DELETE section.                              #
#----------------------------------------------------------------------------#


def removeUser(username):
  try:
    qry = db.session.query(User.userId).filter(func.lower(User.name) == func.lower(username) ).all()
    user_id = User.query.get(qry[0][0])
    db.session.delete(user_id)
    db.session.commit()
    print('The user with name (' + username + ') has been successfully deleted!')
    db.session.close()
    return True
  except:
    db.session.rollback()
    print('An error occurred while deleting ('+ username + ')')
    db.session.close()
    return False


def removeSite(siteName):
    try:
        if (siteName != 'all sites'): 
            qry = db.session.query(Site.siteId).filter(func.lower(Site.siteName) == func.lower(siteName) ).all()
            site_id = Site.query.get(qry[0][0])
            db.session.delete(site_id)
            db.session.commit()
        else:
            db.session.query(Site).delete()
            db.session.commit()
            
        print('The site with name (' + siteName + ') has been successfully deleted!')
        db.session.close()
        return True
    except:
        db.session.rollback()
        print('An error occurred while deleting ('+ siteName + ')')
        db.session.close()
        return False

def removeOutSide_invitedUser(email):
    try:
        print('emailll ' , email)
        qry = db.session.query(Site.siteName).filter(User.name == None , User.emailAddress == email ,
        User.password == None , UserAndSite.User_id == User.userId , UserAndSite.Site_id == Site.siteId).all()
        name = db.session.query(User.name).filter(User.emailAddress == email).all()
        print(qry)
        print(name)

        if len(name) !=0:
            if name[0][0] == None:
                name = None
    
        if len(qry) == 0 and name == None:
            user_id = db.session.query(User.userId).filter(User.emailAddress == email).all()[0][0]
            delete_user = User.query.get(user_id)
            db.session.delete(delete_user)
            db.session.commit()
            db.session.close()

            print('the user with email '+email+'has been successfully delete it!')
            return True
        else:
            print('the user have another site')
            return False
    except Exception as e:
        
        db.session.rollback()
        print(e)
        print('An error occurred while deleting the user with email '+email)
        db.session.close()
        return False
 


def removeSiteFromUser(username_or_email , siteName):
    user_n = username_or_email
    userEmail = username_or_email
    if user_n.find('(') != -1:
        user_n = user_n[user_n.find("(")+1:user_n.find(")")]
    print(username_or_email)
    print(siteName)
    try:
        if (username_or_email.find('@') != -1):
            if username_or_email.find('|') != -1:
                username_or_email = username_or_email.split(' | ')
                userEmail = username_or_email[0]
                user_n = db.session.query(User.name).filter(func.lower(User.emailAddress) == func.lower(userEmail)).all()[0][0]
            else:
                userEmail = username_or_email
                user_n = db.session.query(User.name).filter(func.lower(User.emailAddress) == func.lower(userEmail)).all()[0][0]

        if (siteName != 'all sites'): 
            if user_n is None:
                user_id = db.session.query(User.userId).filter(func.lower(User.emailAddress) == func.lower(userEmail)).all()
            else:
                user_id = db.session.query(User.userId).filter(func.lower(User.name) == func.lower(user_n)).all()
            site_id = db.session.query(Site.siteId).filter(func.lower(Site.siteName) == func.lower(siteName) ).all()
            qry = db.session.query(UserAndSite.UserAndSite_id).filter(UserAndSite.Site_id == site_id[0][0] ,
            UserAndSite.User_id == user_id[0][0]).all()
            print(qry)
            UserAndSite_id = UserAndSite.query.get(qry[0][0])
            db.session.delete(UserAndSite_id)
            db.session.commit()
        else:
            user_id = db.session.query(User.userId).filter(func.lower(User.name) == func.lower(user_n)).all()
            qry = db.session.query(UserAndSite.UserAndSite_id).filter(UserAndSite.User_id == user_id[0][0]).all()
            for i in range(len(qry)):
                UserAndSite_id = UserAndSite.query.get(qry[i][0])
                db.session.delete(UserAndSite_id)
                db.session.commit()
        
        print('The site with name (' + siteName + ') with appropriate username has been successfully deleted!')
        db.session.close()
        if userEmail.find('@') != -1:
            removeOutSide_invitedUser(userEmail)
        return True
    except Exception as e:
        
        db.session.rollback()
        print(e)
        print('An error occurred while deleting ('+ siteName + ') with appropriate username!')
        db.session.close()
        return False

def removeVideo(VidoeName):
    try:
        if VidoeName == None:
            print('video name is none type !!')
            return False
        video_id1 = int(VidoeName[VidoeName.find("(")+1:VidoeName.find(")")])
        print(video_id1)
        qry = db.session.query(Video.video_id).filter(Video.video_id == video_id1)
        print(qry.all())
        if len(qry.all()) == 0:
            print('There is no video with name '+VidoeName)
            return False 
        else:
            video_id = Video.query.get(qry.all()[0][0])
            db.session.delete(video_id)
            db.session.commit()
            db.session.close()
            print('Video with name '+VidoeName+' has been successfully deleted!')
            return True
    except:
        db.session.rollback()
        print('An error occurred while deleting video with name '+VidoeName)
        return False



#----------------------------------------------------------------------------#
#                               UPDATE section.                              #
#----------------------------------------------------------------------------#


def PasswordReset(email , password):

    try:
        qry = db.session.query(User).filter(func.lower(User.emailAddress) == func.lower(email)).all()
        if len(qry) == 0:
            print('User not found!')
            return False
        else:
            if password != None:
                password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            qry = db.session.query(User).filter(User.emailAddress == email).update({User.password : password})
            db.session.commit()
            db.session.close()
            print(email + ' password\'s has been successfully updated')
            return True
    except:
        db.session.rollback()
        print('Error updating the password for ' + email)
        return False
    

def UpdateSiteName(OldSiteName , newSiteName):
    try:
        OldSiteName = OldSiteName.strip()
        newSiteName = newSiteName.strip()

        if OldSiteName.lower() == newSiteName.lower():
            qry1 = db.session.query(Site.siteId).filter(func.lower(Site.siteName) == func.lower(OldSiteName)).all()
            db.session.query(Site).filter(Site.siteId == qry1[0][0]).update({Site.siteName : newSiteName})
            db.session.commit()
            db.session.close()
            print(OldSiteName + ' has been successfully updated with ' + newSiteName)
            return True
        
        qry1 = db.session.query(Site.siteId).filter(func.lower(Site.siteName) == func.lower(OldSiteName)).all()
        qry2 = db.session.query(Site.siteId).filter(func.lower(Site.siteName) == func.lower(newSiteName)).all()
        if len(qry1) == 0:
            print('Site not found!')
            return False
        elif len(qry2) > 0:
            print('There is a site with this name!')
            return False
        else:
            db.session.query(Site).filter(Site.siteId == qry1[0][0]).update({Site.siteName : newSiteName})
            db.session.commit()
            db.session.close()
            print(OldSiteName + ' has been successfully updated with ' + newSiteName)
            return True
    except:
        db.session.rollback()
        print('Error updating the name for ' + OldSiteName)
        return False
    
def changePermission(username , siteName , newRole):

        user_id1 = db.session.query(User.userId).filter(func.lower(User.name) == func.lower(username) ).all()[0][0]
        site_id = db.session.query(UserAndSite.Site_id).filter(UserAndSite.User_id == user_id1).all()
        for x in site_id:
            x = x[0]
            try:
                site_name = db.session.query(Site.siteName).filter(Site.siteId == x).all()
                query2 = db.session.query(UserAndSite.Role).filter(UserAndSite.User_id == user_id1 , UserAndSite.Site_id == x).all()[0][0]
                if site_name[0][0] == siteName and query2 == 'User' and newRole == 'Admin':
                    db.session.query(UserAndSite).filter(UserAndSite.User_id == user_id1 ,
                    UserAndSite.Site_id == x).update({UserAndSite.Role : newRole})
                    db.session.commit()
                    db.session.close()
                    print('The role for '+ username + ' is changed to '+ newRole + ' successfully!')
                    return True
                elif site_name[0][0] == siteName and query2 == 'Admin' and newRole == 'User':
                    db.session.query(UserAndSite).filter(UserAndSite.User_id == user_id1 ,
                    UserAndSite.Site_id == x).update({UserAndSite.Role : newRole})
                    db.session.commit()
                    db.session.close()
                    print('The role for '+ username + ' is changed to '+ newRole + ' successfully!')
                    return True
            except: 
                    db.session.rollback()
                    print('Error updating the Role for ' + username)
                    return False        


def updateUsername(old_username , new_username):
    try:
        old_username = old_username.strip()
        new_username = new_username.strip()

        qry = db.session.query(User).filter(func.lower(old_username) == func.lower(User.name))
        qry2 = db.session.query(User).filter(func.lower(new_username) == func.lower(User.name))

        if len(qry.all()) == 0:
            print('we did not found user with name ' + old_username)
            return False
        elif old_username.lower() == new_username.lower():
            qry.update({User.name : new_username} , synchronize_session='fetch')
            db.session.commit()
            db.session.close()
            print(old_username + ' has been changed to '+ new_username)
            return True
        elif len(qry2.all()) > 0:
            print('the username ' + new_username + ' already exists !')
            return False
        else:
            qry.update({User.name : new_username} , synchronize_session='fetch')
            db.session.commit()
            db.session.close()
            print(old_username + ' has been changed to '+ new_username)
            return True
    except Exception as e: 
        db.session.rollback()
        print(e)
        print('Error updating the name for ' + old_username)
        return False



def getVideoId():
    qry = db.session.query(func.max(Video.video_id)).all()
    print("Error Hereeeeeeeeeeeee",qry)
    print("Error Hereeeeeeeeeeeee",type(qry))
    if qry[0][0] == None:
        return 1
    else:
        return qry[0][0]+1

def update_site_in_Video(old_site , new_site , video_name):

    old_siteId = db.session.query(Site.siteId).filter(Site.siteName == old_site).all()
    new_siteId = db.session.query(Site.siteId).filter(Site.siteName == new_site).all()

    try:
        if len(old_siteId) == 0 or len(new_siteId) == 0:
            if(len(old_siteId) == 0):
                print('we did not found site with name ' + old_site)
                return False
            else: 
                print('we did not found site with name ' + new_site)
                return False
        else:
            video_id = int(video_name[video_name.find("(")+1:video_name.find(")")])
            qry = db.session.query(Video).filter(Video.video_id == video_id ,
            Video.site_id == old_siteId[0][0])
            
            if (len(qry.all()) == 0):
                print('Erorr : there is no '+old_site + ' site with video name '+ video_name)
                return False
            else:
                qry.update({Video.site_id : new_siteId[0][0]})
                db.session.commit()
                db.session.close()
                print(old_site + ' has been changed to '+ new_site)
                return True
    except: 
        db.session.rollback()
        print('Error updating the siteName for ' + old_site)
        return False
    
def update_date_in_Video(new_date , video_name):
    try:
        video_id = int(video_name[video_name.find("(")+1:video_name.find(")")])
        qry = db.session.query(Video).filter(Video.video_id == video_id)

        if len(qry.all()) == 0:
            print('we did not find video with name '+video_name)
            return False
        else:
            qry.update({Video.date : new_date})
            db.session.commit()
            db.session.close()
            print('The date has been changed successfully!')
            return True
    except:
        db.session.rollback()
        print('Error updating the date for ' + video_name)
        return False


def update_videoName(old_VideoName , new_VideoName):
    try:
        if old_VideoName == None or new_VideoName == None:
            print(' erorr : old_VideoName is None or new_VideoName is None!')
            return False

        old_video_id = int(old_VideoName[old_VideoName.find("(")+1:old_VideoName.find(")")])
        

        qry = db.session.query(Video).filter(Video.video_id == old_video_id)
        if len(qry.all()) == 0:
            print('there are no video with name '+ old_VideoName)
            return False
        else:
            
            qry.update({Video.video_name : new_VideoName})
            db.session.commit()
            db.session.close()
            print('The video name has been changed successfully!')
            return True
    except:
        db.session.rollback()
        print('Error updating the video name for ' + old_VideoName)
        return False

def update_Displayname(username , new_displayname):

    try:
        username = username.lower()
        qry = db.session.query(User).filter(func.lower(User.name) == func.lower(username)).all()
        if len(qry) == 0:
            print('User not found!')
            return False
        else:
            qry = db.session.query(User).filter(func.lower(User.name) == func.lower(username)).update(
                {User.display_name : new_displayname} , synchronize_session='fetch')
            db.session.commit()
            db.session.close()
            print(username + ' display name has been successfully updated')
            return True
    except:
        db.session.rollback()
        print('Error updating the displayname for ' + username)
        return False


def updateEmail(username, new_email):
    try:
        username = username.strip()
        new_email = new_email.strip()
        username = username.lower()
        new_email = new_email.lower()

        qry = db.session.query(User).filter(func.lower(username) == func.lower(User.name))
        qry2 = db.session.query(User).filter(func.lower(new_email) == func.lower(User.emailAddress))

        print(qry.all())
        print(len(qry2.all()))

        if len(qry.all()) == 0:
            print('we did not found user with name ' + username)
            return False
        elif len(qry2.all()) > 0:
            print('the username ' + new_email + ' already exists !')
            return False
        else:
            qry.update({User.emailAddress : new_email} , synchronize_session='fetch')
            db.session.commit()
            db.session.close()
            print('the email has been changed to '+ new_email)
            return True
    except Exception as e: 
        db.session.rollback()
        print(e)
        print('Error updating the email for ' + username)
        return False


def updatePassword(username , new_password):
    try:
        username = username.lower()
        qry = db.session.query(User).filter(func.lower(User.name) == func.lower(username)).all()
        if len(qry) == 0:
            print('User not found!')
            return False
        else:
            if new_password != None:
                new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

            qry = db.session.query(User).filter(func.lower(User.name) == func.lower(username)).update({User.password : new_password} , synchronize_session='fetch')
            db.session.commit()
            db.session.close()
            print(username + ' password has been successfully updated')
            return True
    except:
        db.session.rollback()
        print('Error updating the password for ' + username)
        return False
        
#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
#if __name__ == '__main__':
    #new
    #totalNumberOfVistors('all sites' , 'ali', '2021-01-02' , '2021-12-02')
    #AvgTimeSpent('retail store', 'ali', '2021-01-02' , '2021-12-02')
    #SiteWithMaxVistors('jewelry store', '2021-01-01' , '2021-12-02')
    #SiteWithFewestVistors('ali', '2021-01-02' , '2021-07-02')
    #FiveMostDaysOfVistors('ali', 'clothes store', '2021-01-02' , '2021-12-02')
    #FiveFewestDaysOfVistors('ali' , 'all sites' , '2021-01-02' , '2021-12-02')
    #UserSites('ali' , 'all')
    #userWithoutRelation('clothes store')

    #usernamesInTheSite('turky' ,'juice store' , 'all')
    #LoginChecker('Ali1' , '12')
    #CheckRole('ali' , 'jewelry store')
    #removeUser('ali')
    #UserRelation('ali')
    #removeSite('all sites')

    #removeSiteFromUser('maged_email@mozej.com | invited' , 'juice store')
    #removeVideo('vid12')
    #PasswordReset('khalid' , 'iferjf@outlook.com' , '23434ssa')
    #updatePassword('Tu3rky' , '2121')

    #addToUser('test' ,'test w' , 'test@outlook.com' , '123')
    #EmailAndUserCheaker('ali' , 'oekfroe@h.com')
    #addToSite('ali' , "ResturanT")

    #removeOutSide_invitedUser('loly3@mozej.com')
    #displayHeatMap('test' , 'all sites' , '2022-03-23' , '2022-03-23')
    #updateEmail('khaleD' , 'TralLL39_email@mozej.com')
    #updateUsername("Ali" , "MageD4747")
    #EmailCheaker('tral474@outlook.com')
    #UserChecker('trok4747')
    
    #inviteUserToSite('test@outlook.com' , 'jewelry store' , 'Admin' , 'ali')
    #acceptSite('ali' , 'Resturant')
    #UserPendingSites('mohammed')
    #addToPermission('khaled' , 'mgwhart' , 'Admin')
    #AvgVistorsPerDay('ali' , 'Resturant' , '2021-1-2' , '2021-12-2')
    #AvgVistorsPerMonth('ali' , 'fruit shop' , '2021-1-2' , '2021-12-2')
    #yaddToVideo('retail store' , 5435 , 3493 , '2021-9-2' , 'plpl' , 'vido19')
    #update_site_in_Video('juice store' , 'mlabs' , 'vid11')
    #update_date_in_Video('2021-5-02' , '2021-11-02', 'vid10')
    #update_videoName('vid11','vid12')
    #updateUsername('khaled', 'maged1')
    #VideoName_with_siteName_List('ali')
    #checkUserSite('ali')
    #UpdateSiteName('vegetables Store' , 'ResturanT1')
    #defaultDate('dede')
    #changePermission('khaled', 'mlabs' , 'User')
    #SiteWithoutResult('mlabs')
    #manager.run()
