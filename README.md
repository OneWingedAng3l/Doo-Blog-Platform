Description
    A User blog where users can sign up and post comment and like their posts as well as comment at other users blogs.

Requirements:
    Step 1: Create a Basic Blog

    Blog must include the following features:
        Front page that lists blog posts.
        A form to submit new entries.
        Blog posts have their own page.
    View instructions and solutions here.

    Step 2: Add User Registration

        Have a registration form that validates user input, and displays the error(s) when necessary.
        After a successful registration, a user is directed to a welcome page with a greeting, “Welcome, ” where is a name set in a cookie.
            If a user attempts to visit the welcome page without being signed in (without having a cookie), then redirect to the Signup page.
        Watch the demo for more details.
        Be sure to store passwords securely.

    Step 3: Add Login

        Have a login form that validates user input, and displays the error(s) when necessary.
        After a successful login, the user is directed to the same welcome page from Step 2.
        Watch the demo for more details.

    Step 4: Add Logout

        Have a logout form that validates user input, and displays the error(s) when necessary.
        After logging out, the cookie is cleared and user is redirected to the Signup page from Step 2.
        Watch the demo for more details.

    Step 5: Add Other Features on Your Own

        Users should only be able to edit/delete their posts. They receive an error message if they disobey this rule.
        Users can like/unlike posts, but not their own. They receive an error message if they disobey this rule.
        Users can comment on posts. They can only edit/delete their own posts, and they should receive an error message if they disobey this rule.

How to Run:
    1. Visit http://aruserblog.appspot.com
    2. Import the project on your Google App Engine app and jusr hit Run :)

Project Structure:
    lib folder:
        contains the extra libraries used in the project
        static folder:
            - css: holds the css files
            - img: holds the images files
            - js: holds the js files
        templates folder: has the .html files
        main.py: holds the project logic
        appengine_config.py: used to import the extra libraries in the project

Implemented Frameworks and Libraries:
        1. webapp2
        2. jinja2

Implemented Libraries (EXTRA):
    1. pybycryot - used for hashing user passwords in the database
    2. wtforms - used for display and validating the forms
    3. jQuery - under the js folder. used for shorting down javascript code.
    4. jQuery UI - userd for displaying tooltips.

Future Features:
    1. add https
    2. implement search logic
    3. implement CSRF protection
    4. implement bootstrap framework (this was not done till now  due to the project requiring custom css)
    5. implement admin panel
    6. implement connection with social networks
    7. refactor queries to use only filters instead of GQL
    8. solve scaling issue described below.
    9. implement a dev. show. live. enviroment

Known Issues:
1. Strong Consistency (https://cloud.google.com/appengine/docs/python/datastore/structuring_for_strong_consistency)
   Since we are not using ancestor queries that will updatate IMEDIATELLY all the servers that runinng the app LIKE / Delete Buttons
   need a refresh after they have been pushed.
   "The reason for this behavior, especially if you are in the dev server, is that GAE now simulates eventual consistency.
   Basically, this means that your newly added guestbook entry will not be present across all servers that your app is running
   on right away. Some of your users might see it instantly, some might not. A good way to make sure you're getting the latest data
   is to refresh the page and force the app to load it...but of course you can't expect users to like that!
   The new guestbook tutorial uses ancestor queries instead, which enforces strong consistency. In other words,
   users will see updates right away, no need to refresh the page!"

   SOLUTION: For the DEV enviroment ONLY there has been added a time.sleep(0.1) before each redirect.



