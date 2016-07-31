from google.appengine.ext import db

#
#   Database Classes
#


class User(db.Model):
    name = db.StringProperty(required=True)
    surname = db.StringProperty(required=True)
    email = db.EmailProperty(required=True)
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    dateTimeRegistered = db.DateTimeProperty(auto_now_add=True)


class Posts(db.Model):
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    accessLevel = db.StringProperty(required=True)
    author = db.IntegerProperty(required=True)
    dateTimeCreated = db.DateTimeProperty(auto_now_add=True)
    dateTimeModified = db.DateTimeProperty(auto_now=True)


class Likes(db.Model):
    postID = db.IntegerProperty(required=True)
    userID = db.IntegerProperty(required=True)
    likesCount = db.IntegerProperty(required=True)


class Comments(db.Model):
    content = db.TextProperty(required=True)
    authorID = db.IntegerProperty(required=True)
    postID = db.IntegerProperty(required=True)
    dateTimeCreated = db.DateTimeProperty(auto_now_add=True)
    dateTimeModified = db.DateTimeProperty(auto_now=True)
