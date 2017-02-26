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
import webapp2
import jinja2
import cgi
import os
import re
import time

from google.appengine.ext import db

#setting up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class BlogPost(db.Model):
    title = db.StringProperty(required = True)
    post_content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class MainPage(Handler):
    pass


class BlogPage(Handler):
    def render_base(self, title="", post_content=""):
        blog_posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 5")
        self.render("blog-page.html", title=title, post_content=post_content, blog_posts=blog_posts)

    def get(self):
        self.render_base()


class NewPost(Handler):
    def get(self):
        self.render("new-post.html")

    def post(self):
        title = self.request.get("title")
        post_content = self.request.get("post_content")

        if title and post_content:
            blogpost = BlogPost(title=title, post_content=post_content)
            blogpost.put()
            time.sleep(0.25)

            self.redirect("/blog/" + str(blogpost.key().id()))
        else:
            error = "You need both a title and post content."
            self.render("new-post.html", title=title, post_content=post_content, error=error)


class ViewPostHandler(Handler):
    def get(self, id):
        blog_posts = BlogPost.get_by_id(int(id))
        self.render("blog-posts.html", blog_posts=blog_posts)



#        self.write(BlogPost.get_by_id(int(id)))
#
#        if blogpost:
#            self.render("blog-posts.html", title=title, post_content=post_content)
#        else:
#            self.write("Error 404: Page does not exist")



app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', BlogPage),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
