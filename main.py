import webapp2
import jinja2
import os

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def get(self):
        blog = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        t = jinja_env.get_template("post.html")
        response = t.render(blogs = blog)

        self.response.write(response)

class PostForm(Handler):
    def render_post_form(self, subject="", content="", error=""):
        self.render("form.html", subject=subject, content=content, error=error)

    def get(self):
        self.render_post_form()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            a = Blog(subject = subject, content = content)
            a.put()

            # self.redirect("/blog")
            response = "<h1>" + subject + "</h1>"+ "<div>" + content + "</div>"
            self.response.write(response)

        else:
            error = "You have to enter text in both fields to submit!"
            self.render_post_form(subject, content, error)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        post = Blog.get_by_id(int(id))

        if post:
            response = "<h1>" + post.subject + "</h1>"+ "<div>" + post.content + "</div>"
            self.response.write(response)
        else:
            error="<h1>That id does not match a known id, please try a different id.</h1>"
            self.response.write(error)


app = webapp2.WSGIApplication([
        ('/', MainPage),
        ('/blog', MainPage),
        ('/newpost', PostForm),
        webapp2.Route('/blog/<id:\d+>', ViewPostHandler)

], debug=True)
