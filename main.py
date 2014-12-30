#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# name: Terrence Kuo
# Description: This is a working blog using Google App Engine Launcher. 

import os
import webapp2
import jinja2
from google.appengine.ext import db

# concat the current directory with the templates directory
# the templates directory contains all the the templates (html files)
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
# create a jinja2 environment from the templates directory
# when we render templates, jinja is going to look for templates in the template_dir
jinja2_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

# create a blog database type that has a subject, content, time created, and time modified
class Post(db.Model):
	# creates String type
    subject = db.StringProperty(required = True)
    # creates a text type
    content = db.TextProperty(required = True)
    # creates a date-time object
    created = db.DateTimeProperty(auto_now_add = True)
    # creates a date-time object
    last_modified = db.DateTimeProperty(auto_now = True)

# defines the blog key
def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Handler(webapp2.RequestHandler):
	# sends information to the browser
	# the *a is used to pass in a tuple. a stands for arguements
	# the **kw is used to pass in a dictionary. kw stands for keywords
	def write(self, *a, **kw):
		self.response.write(*a, **kw);

	def render_str(self, template, **params):
		# uses the created jinja2 enivronment and loads the template which is a html file
		t = jinja2_env.get_template(template)
		# provides the template (html file) with parameters
		# returns a string
		return t.render(params);

	def render(self, template, **kw):
		# calls redner_str and wraps it in self.write which actually sends it to browser
		self.write(self.render_str(template, **kw));

# creates the new post webpage
class NewPostHandler(Handler):
	# intialize the subject, content, and error with empty strings
	def format(self, subject ="", content ="", error=""):
		self.render("new_post.html", subject = subject, content=content, error =error);

	def get(self):
		# create empty post page
		self.format();

	def post(self):
		# obtain parameters from user based on the html page new_post.html
		subject = self.request.get("subject");
		content = self.request.get("content");

		# checks if subject and content are intiated
		if subject and content:
			# create database instances 
			p = Post(parent = blog_key(), subject = subject, content = content)
			# stores the instance in the database
			# when this happens, googles database gives you an id
			p.put();

			# .key() is google way of getting the whole object
			# .id gets the id of the particular key
			x = str(p.key().id());

			# redirect to the page with all the blog listings
			# str(p.key().id()) is used to optain the id of a post
			self.redirect("/blog/%s" %x);
		else:
			error = "Need to include both subject and blog"
			self.format(subject, content, error);

# webpage with all the blog listings
class BlogListingHandler(Handler):
	def format(self):
		# runs the query to get cursor
		entries = db.GqlQuery("select * from Post order by created desc limit 10")
		# creates the new webpage containing the blog listings
		self.render("blog_listing.html", entries = entries);

	def get(self):
		self.format()

# webpage showing the blog entered
class PostPageHandler(Handler):
	# post_id comes from the ([0-9]+) from the ('/blog/([0-9]+)', PostPageHandler),
    def get(self, post_id):
    	# to look up a post 
    	# first you make a key: db.Key.from_path() 
    	# find the "Post" with the int(post_id)
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        # look up a particular item
        post = db.get(key)

        if not post:
            self.error(404)
            return

        self.render("post_page.html", post = post)

# each of the '/blog/newpost' is a regular expression
app = webapp2.WSGIApplication([
    ('/blog/newpost', NewPostHandler),
    ('/blog', BlogListingHandler),
    ('/blog/([0-9]+)', PostPageHandler),
], debug=True)
