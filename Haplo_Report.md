Haplo App
=========

###Abstract

*As part of an application to Haplo, I designed and built the base features of story-telling app over the course of two afternoons/evenings, with a day of planning/thought.  This report contains details of the brief, design and implementation of the app. The specific order of implementation can be tracked on [GitHub](https://github.com/condnsdmatters/haplo-task)*

###Brief 
1. Design and implement a web-based app for writing 'multi-scenario' stories
2. The user interface should:
    + allow for the input of four different sentences, following a core parent sentence
    + present each inputted sentence with a link to a page with it now as a parent, with its own children
    + provide a means to move to the very start of the story 
3. The project brief is language and framework agnostic, though there should be no client-side javascript

###Design 

As with any project of a substantial size, I approached design by starting trying to answer some questions before implementing: 

1. **Usage:** What was the likely use case of the project?  What kind of unforseen functionalities might be needed? Who would be using the app?
2. **Scale**: What was necessary scale of the project? Should there be room for expansion in size?
3. **Restrictions**: Are there any (possibly hidden) constraints on the problem? Must it look a certain way, use a certain technology or perform better than a certian benchmark?

As an interview problem (rather than a used product), the answers to these kind of questions were rather abstract, or at least, hypothetical. 

1. I felt this app would hypothetically be used by writers, looking to flesh out different stories. As such it would be almost inevitable the app should be able to handle more than one story, or have more than one user - if possible the architecture should allow for this. If there was time, this feature (surplus to brief) could be added.
2. As a quick app, it was probably meant to be quite small, but since the usage case was unknown, there should be good architecture for expansion, and the code should be clear, modular and maintainable. A small database should be used for data.
3. The constraints seemed pretty clear, just to use shortcuts where possible and no server side javascript. The program should be runnable on a Unix OS.

At this point I chose my tools and began to design the specific implementation of how the app would function. 

###Implementation


#####Tools
The app was implemented in Python 2.7 using Flask as the microframework.  As a very small framework, Flask is very suited to these kind of projects, and has well documented API with also plenty of handy tutorial examples.

I decided to use a SQLite database to store the information, with this framework. Not only is SQLite readily available on the Mac OS X, but its small size also made it an ideal candidate for this small project and I have experience with these databases.

#####Code

The app was built in two bulk stages:

 1. All the requisite functionality was designed and built (~5hrs)
 2. Multi-user functionality was added and code refactored (~4hrs)

 In stage 1:
 
* I started by creating a virtual environment and building the basic archicture of a moderately-sized Flask app: having a separate `__init__.py` and `views.py`, with internal `templates` and `static` directories. This would provide good structure for potentially expanding the app at a later time, if necessary. 

* The `schema.sql` of the database was written, designed so that the information could be stored as a tree, again leaving as much flexibility for future functionality. Each "sentence" would contain a reference to *both* parents and children (to potentially minimise look up in future), and also a `user_id` (which would be always be 0 initially).

* In terms of the `views.py`, I decided almost everything would be rendered with one method, `index()`, and a session variable would carry references to the specific info to be rendered (`node_id` and `user_id`). This design would minimize the amount of code written, make the most of the inherent symmettry of the problem, whilst allowing for multiple users at one time.

* The `index()` would fetch the `message`s and `node_id`s for a given `node_id` and its `children`.  If the children's messages are `NULL`, these would render as forms, else as hyperlinks. 

* The `POST` request from each form edits the database to add its message, then creates 4 new children for that node and reloads the original page (rendering a hyperlink instead of a form). The hyperlink issues a `GET` request, changing the `node_id` and reloading the page. Going ""Back to Start"", simply changes the `node_id` to `0`, which triggers a search for the first node in the index method. 

* The html was written in sections, with templates expanding each other (thanks to Flask's Jinja model) which kept the html easy to follow and modular.

In stage 2:

* The `schema.sql` was altered to add new users, and methods to add users and create logins were written. Although this was surplus to brief, I felt a login would be an absolutely vital part of any such app, and (having never written such a feature) found it both instructive and enjoyable to implement it.

*  Docstrings were added and variables and methods renamed. This added to the code clarity.    e.g. naming two main variables `parent` and `children` left a subtle ambiguity as to their relationship: 

       (parent -> node -> children)
       or (parent -> children)
 As such it was clearer to rename variables to just `node` and `children` 

* A `style.css` file was quickly added to `static` directory to minorly improve the views.


###Shortcuts and Caveats

As someone who had never written a Flask app, except for the tutorial, I used a number of shortcuts that helped.

* **SHORTCUT:** Whenever I hit a stumbling block, I would consult my Flask tutorial, looking at my code for any lessons to be drawn. This was particularly useful in knowing how to structure the apps modules, and also the html.

* **SHORTCUT:** I effectively used the `static/style.css` file from the tutorial as a quick fix to get a vaguely pleasing visual for minimal effort.

* **SHORTCUT/CAVEAT**: The reason new blank messages are created, stored and then rendered, rather than only stored when written in, was to overcome the problem of keeping sentences in the same orientation/order around the core sentence.  This quick-fix saved writing time, but could conceivably become a big memory problem if stories become very long.

* **SHORTCUT/CAVEAT:** There are certain redundancies in the data stored. Storing both a node's children and its parents is unnecessary, and indeed only the parent field is used. Both were included to keep flexibility, but again this is at the cost of memory. Also searches were definitely sub-optimal as no indexing was used, and this could be improved.

+ **CAVEAT**: As this app is very small, testing could be done pretty much by hand. Before expanding tests would certainly need to be built, using the internal unittests availabilities in Flask.

+ **CAVEAT**: As someone with limited app experience it is possible the MVC model was not properly used (I'm am only vaguely aware of the paradigm). As such perhaps the database helper functions should have been in a separate module, but they were kept together for ease of reading.

###Lessons Learnt

All in all I think this task was a valuable test in a few things:

1. Good code practice: Is code modular? Maintainable? Well designed? Easy to read? Clear? Is it well named? Is it documented? 
2. Appoaches to problem solving: What do you do when first presented with a problem? How do you proceed with finding a solution?. 
3. Ability to work with frameworks/3rd party code: How good is you knowledge of a certain framework, or how well can you work with code thats not your own?
4. Can you code quickly where necessary? Do you use shortcuts? Can you deliver on schedule?
5. Can you communicate your ideas and designs to clients?

All in all, I found this exercise very enjoyable, whilst also valuable practice in simple app design and development. I look forward to discussing the outcome of this task with you, in the near future.

 
