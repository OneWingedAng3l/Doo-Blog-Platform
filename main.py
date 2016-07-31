#!/usr/bin/env python
import os
import webapp2
import logging
import jinja2
import time
from models import (User, Posts, Likes, Comments)
from forms import (RegisterForm, LoginForm, PostsForm, CommentForm)
from pybcrypt import bcrypt
from google.appengine.ext import db
from webapp2_extras import sessions


#
#   SetUp Enviroment
#

templateDir = os.path.join(os.path.dirname(__file__), 'templates')
jinjaEnv = jinja2.Environment(loader=jinja2.FileSystemLoader(templateDir),
                              autoescape=True)

#
#   Main Handler Class (Basically the Render Page Simplified)
#


class Handler(webapp2.RequestHandler):
    def handle_404(self, request, response, exception):
        logging.exception(exception)
        response.write(jinjaEnv.get_template("404.html").render())
        response.set_status(404)

    def handle_500(self, request, response, exception):
        logging.exception(exception)
        response.write(jinjaEnv.get_template("500.html").render())
        response.set_status(500)

    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinjaEnv.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()


#
#   Page Classes (Each Class Represents a page)
#

class Initialize(Handler):
    def get(self):
        username = self.session.get("username")
        allUsers = db.GqlQuery("SELECT * FROM User")
        commentForm = CommentForm(self.request.POST)
        if username:
            time.sleep(0.1)
            # get the user ID
            user = db.GqlQuery("SELECT * FROM User WHERE username='%s'"
                               % username)
            userID = user.get().key().id()
            # Get all the posts the user has already liked
            postsUserLiked = db.GqlQuery("SELECT * FROM Likes WHERE userID=%d"
                                         % userID)
            # Get all (public and private) last 5 posts
            allPosts = db.GqlQuery("SELECT * FROM Posts "
                                   "ORDER BY dateTimeCreated DESC LIMIT 5")
            self.render("index.html", username=username, userID=userID,
                        post=allPosts, author=allUsers,
                        likedPosts=postsUserLiked, form=commentForm)
        elif not username:
            pubPosts = db.GqlQuery("SELECT * FROM Posts "
                                   "WHERE accessLevel='pub' LIMIT 5")
            self.render("index.html", post=pubPosts, author=allUsers)


class NewPosts(Handler, webapp2.RequestHandler):
    def get(self):
        if self.session.get("username"):
            form = PostsForm(self.request.GET)
            self.render("newPost.html", form=form,
                        username=self.session.get("username"))
        else:
            self.redirect("/register")

    def post(self):
        if self.session.get("username"):
            form = PostsForm(self.request.POST)
            # Get the userID in order to associate it with the post
            username = self.session.get("username")
            user = db.GqlQuery("SELECT * FROM User WHERE username='%s'"
                               % username)
            userID = user.get()
            userID = userID.key().id()
            # if the form is valid add the post to the datastore and then
            # redirect to the detail View of the post.
            if form.validate():
                newPost = Posts(title=form.title.data,
                                content=form.content.data,
                                accessLevel=form.accessLevel.data,
                                author=userID)
                newPost.put()
                self.redirect("/post/%s" % newPost.key().id())
            else:
                self.render("newPost.html", form=form,
                            username=self.session.get("username"))
        else:
            self.redirect("/register")


class DetailPostView(Handler, webapp2.RequestHandler):
    def get(self, postID):
        if self.session.get("username"):
            time.sleep(0.2)
            comment_form = CommentForm(self.request.POST)
            # get all the users
            all_users = db.GqlQuery("SELECT * FROM User")
            # get the post key
            key = db.Key.from_path('Posts', int(postID))
            post = db.get(key)
            # get the current user ID
            user = db.GqlQuery("SELECT * FROM User WHERE username='%s'"
                               % self.session.get("username"))
            user_id = user.get()
            user_id = user_id.key().id()
            # has the user liked this post
            posts_liked_by_user = db.GqlQuery("SELECT * FROM Likes "
                                              "WHERE userID=%d" % user_id)
            # get all the comments for the specifc post
            post_comments = db.GqlQuery("SELECT * FROM Comments "
                                        "WHERE postID=%d "
                                        "ORDER BY"
                                        " dateTimeCreated" % int(postID))
            self.render("detailview.html", post=post,
                        username=self.session.get("username"),
                        author=all_users,
                        likedPosts=posts_liked_by_user,
                        userID=user_id,
                        form=comment_form,
                        comments=post_comments)
        else:
            self.redirect("/register")


class EditPost(Handler, webapp2.RequestHandler):
    def get(self, postID):
        if self.session.get("username"):
            user = db.GqlQuery("SELECT * FROM User WHERE username='%s'"
                               % self.session.get("username"))
            userID = user.get().key().id()
            key = db.Key.from_path('Posts', int(postID))
            post = db.get(key)
            if post.author == userID:
                # instantiate the form
                form = PostsForm(self.request.POST)
                # get the post data
                form.title.data = post.title
                form.content.data = post.content
                form.accessLevel.data = post.accessLevel
                self.render("editPost.html", form=form,
                            post=post,
                            username=self.session.get("username"))
            elif post.author is None or post.author != userID:
                self.redirect("/")
        else:
            self.redirect("/")
            # self.session.add_flash("Trying to hack us ?!? :D")
            # todo: Add an error function with the appropriate messages!

    def post(self, postID):
        if self.session.get("username"):
            user = db.GqlQuery("SELECT * FROM User WHERE username='%s'"
                               % self.session.get("username"))
            userID = user.get().key().id()
            form = PostsForm(self.request.POST)
            key = db.Key.from_path('Posts', int(postID))
            post = db.get(key)
            if form.validate() and form.submit.data and int(post.author) == \
                    int(userID):
                post.title = form.title.data
                post.content = form.content.data
                post.accessLevel = form.accessLevel.data
                post.put()
                self.redirect("/post/%s" % post.key().id())
            elif form.cancel.data:
                self.redirect("/post/%s" % post.key().id())
            else:
                self.redirect("/")
        else:
            self.redirect("/")


class DeletePost(Handler, webapp2.RequestHandler):
    def get(self, postID):
        user = db.GqlQuery("SELECT * FROM User WHERE username='%s'"
                           % self.session.get("username"))
        userID = user.get().key().id()
        key = db.Key.from_path('Posts', int(postID))
        post = db.get(key)
        if self.session.get("username") and int(post.author) == int(userID):
            try:
                db.delete(post)
            finally:
                self.redirect("/")
        else:
            self.redirect("/")
            # todo: Add an error function with the appropriate messages!


class EditComment(Handler, webapp2.RequestHandler):
    def get(self, commentID):
        if self.session.get("username"):
            user = db.GqlQuery("SELECT * FROM User WHERE username='%s'"
                               % self.session.get("username"))
            userID = user.get().key().id()
            key = db.Key.from_path('Comments', int(commentID))
            comment = db.get(key)
            if int(comment.authorID) == int(userID):
                # instantiate the form
                form = CommentForm(self.request.POST)
                # get the post data
                form.comment.data = comment.content
                self.render("editComment.html",
                            form=form,
                            comment=comment,
                            username=self.session.get("username"))
            else:
                self.redirect("/")
        else:
            self.redirect("/")
            # todo: Add an error function with the appropriate messages!

    def post(self, commentID):
        form = CommentForm(self.request.POST)
        if self.session.get("username"):
            user = db.GqlQuery("SELECT * FROM User WHERE username='%s'"
                               % self.session.get("username"))
            userID = user.get().key().id()
            key = db.Key.from_path('Comments', int(commentID))
            comment = db.get(key)
            if form.validate() and int(comment.authorID) == int(userID):
                comment.content = form.comment.data
                comment.put()
                self.redirect("/")
            else:
                self.redirect("/")
        else:
            self.redirect("/")


class DeleteComment(Handler, webapp2.RequestHandler):
    def get(self, commentID):
        # protection so unauthorized people cannot delete posts
        # basically if the current user is not
        # the comment owner just redirect him.
        if self.session.get("username"):
            key = db.Key.from_path('Comments', int(commentID))
            comment = db.get(key)
            post = comment.postID
            user = db.GqlQuery("SELECT * FROM User WHERE username='%s'"
                               % self.session.get("username"))
            userID = user.get().key().id()
            if int(userID) == int(comment.authorID):
                try:
                    db.delete(comment)
                finally:
                    self.redirect("/post/%s" % post)
            else:
                self.redirect("/")
        else:
            self.redirect("/")
            # todo: Add an error function with the appropriate messages!


class LikePost(Handler, webapp2.RequestHandler):
    def get(self, postID):
        if self.session.get("username"):
            user = db.GqlQuery("SELECT * FROM User WHERE username='%s'"
                               % self.session.get("username"))
            userID = user.get().key().id()
            key = db.Key.from_path('Posts', int(postID))
            post = db.get(key)
            if int(post.author) != int(userID):
                new_post_like = Likes(postID=int(postID), userID=int(userID),
                                      likesCount=1)
                new_post_like.put()
                self.redirect("/")
            else:
                self.redirect("/")
        else:
            self.redirect("/")
            # todo: Add an error function with the appropriate messages!


class UnlikePost(Handler, webapp2.RequestHandler):
    def get(self, postID):
        user = db.GqlQuery("SELECT * FROM User WHERE username='%s'"
                           % self.session.get("username"))
        userID = user.get().key().id()
        key = db.Key.from_path('Posts', int(postID))
        post = db.get(key)
        if self.session.get("username") and post.author != userID:
            like = db.GqlQuery("SELECT * FROM Likes "
                               "WHERE userID = %d "
                               "AND postID = %d"
                               % (int(userID), int(postID)))
            like = like.get().key()
            db.delete(like)
            self.redirect("/")
        else:
            self.redirect("/")
            # todo: Add an error function with the appropriate messages!


class CommentPost(Handler, webapp2.RequestHandler):
    def get(self):
        if not self.session.get("username"):
            self.redirect("/")

    def post(self, postID):
        if self.session.get("username"):
            commentForm = CommentForm(self.request.POST)
            user = db.GqlQuery("SELECT * FROM User WHERE username='%s'"
                               % self.session.get("username"))
            userID = user.get().key().id()
            if commentForm.validate():
                newComment = Comments(content=commentForm.comment.data,
                                      authorID=int(userID),
                                      postID=int(postID))
                newComment.put()
                self.redirect("/post/%s" % postID)
            else:
                self.redirect("/")
        else:
            self.redirect("/")
            # todo: Add an error function with the appropriate messages!


class PopularPosts(Handler, webapp2.RequestHandler):
    def get(self):
        self.render("popularPosts.html")

    def post(self):
        q = self.request.get("username")
        self.response.write(q)


class Search(Handler, webapp2.RequestHandler):
    def get(self):
        self.render("search.html")

    def post(self):
        q = self.request.get("search")
        self.response.write(q)


class Login(Handler, webapp2.RequestHandler):
    def get(self):
        self.render("login.html", form=LoginForm(self.request.GET),
                    username=self.session.get("username"))

    def post(self):
        form = LoginForm(self.request.POST)
        if form.validate():
            # Submit the query in the datastore
            user_record = db.GqlQuery("SELECT * FROM User WHERE username='%s'"
                                      % form.username.data)
            user = user_record.get()
            if user is not None:
                if bcrypt.hashpw(form.passwd.data, user.password)\
                        == user.password:
                    self.session['username'] = form.username.data
                    self.redirect("/")
                elif bcrypt.hashpw(form.passwd.data, user.password)\
                        != user.password:
                    # self.redirect("/")
                    self.render("login.html", form=form,
                                error="Invalid Username Or Password",
                                username=self.session.get("username"))
            elif user is None:
                self.render("login.html", form=form,
                            error="Invalid Username Or Password",
                            username=self.session.get("username"))
        else:
            self.render("login.html", form=form,
                        error="Invalid Username Or Password",
                        username=self.session.get("username"))


class Logout(Handler, webapp2.RequestHandler):
    def get(self):
        self.session.clear()
        self.redirect("/")


class Register(Handler, webapp2.RequestHandler):
    def get(self):
        form = RegisterForm(self.request.GET)
        self.render("register.html", form=form,
                    username=self.session.get("username"))

    def post(self):
        form = RegisterForm(self.request.POST)
        if form.validate():
            # Submit the query in the datastore
            email = db.GqlQuery("SELECT * FROM User WHERE email='%s'"
                                % form.email.data)
            username = db.GqlQuery("SELECT * FROM User WHERE username='%s'"
                                   % form.username.data)
            username, email = username.get(), email.get()
            # if there is no record in the datastore with the provided data
            # create a new user.
            if email is None and username is None:
                hashedPass = bcrypt.hashpw(form.passwd.data, bcrypt.gensalt(2))
                newuser = User(name=form.name.data,
                               surname=form.surname.data,
                               email=form.email.data,
                               username=form.username.data,
                               password=hashedPass)
                newuser.put()
                # Create the session for the new user
                self.session['username'] = form.username.data
                self.redirect("/")
                # todo: refactor the if to catch both mailError
                # and usernameError at the same time.
            elif email is not None:
                self.render("register.html", form=form,
                            mailError="This Mail Is Already Registered",
                            username=self.session.get("username"))
            elif username is not None:
                self.render("register.html", form=form,
                            usernameError="This Username Is Taken :-(",
                            username=self.session.get("username"))
        else:
            self.render("register.html", form=form,
                        username=self.session.get("username"))


class Admin(Handler, webapp2.RequestHandler):
    def get(self):
        users = db.GqlQuery("SELECT * FROM User")
        self.render("adminPanel.html", users=users,
                    username=self.session.get("username"))


#
#   URL Routing. Basically map each url to the appropriate class.
#


# 'cookie_args': {'secure': 'true'},
config = config['webapp2_extras.sessions'] = {
    'secret_key': 'Hello form w3b app.. This secret key it is! Y0d@',
    'cookie_name': 'ss_rec'
}

app = webapp2.WSGIApplication([
    ('/', Initialize),
    ('/new', NewPosts),
    ('/post/(\d+)', DetailPostView),
    ('/delete/(\d+)', DeletePost),
    ('/delcomment/(\d+)', DeleteComment),
    ('/edit/(\d+)', EditPost),
    ('/editcomment/(\d+)', EditComment),
    ('/like/(\d+)', LikePost),
    ('/unlike/(\d+)', UnlikePost),
    ('/comment/(\d+)', CommentPost),
    ('/popular', PopularPosts),
    ('/search', Search),
    ('/login', Login),
    ('/logout', Logout),
    ('/register', Register),
    ('/admin', Admin)],
     debug=True, config=config)


app.error_handlers[404] = Handler().handle_404
app.error_handlers[500] = Handler().handle_500
