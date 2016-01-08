import os
import urllib

from google.appengine.ext import ndb

import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_RSVP_NAME = 'default_rsvp'

def rsvp_key(rsvp_name=DEFAULT_RSVP_NAME):
    """Constructs a Datastore key for a Guestbook entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('RSVPModel', rsvp_name)

class RSVPModel(ndb.Model):
    """Sub model for representing an author."""
    rsvp = ndb.StringProperty(indexed=False)
    name = ndb.StringProperty(indexed=False)
    number = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class MainPage(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render())


class Invite(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('invite.html')
        self.response.write(template.render())

class RSVP(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('rsvp.html')
        self.response.write(template.render())

    def post(self):
        rsvp_name = self.request.get('rsvp_name',
                                          DEFAULT_RSVP_NAME)
        rsvpModel = RSVPModel(parent=rsvp_key(rsvp_name))

        rsvpModel.rsvp = self.request.get('rsvp')
        rsvpModel.name = self.request.get('name')
        rsvpModel.number = self.request.get('number')
        rsvpModel.put()

        query_params = {'rsvp': rsvpModel.rsvp}
        self.redirect('/thanks?' + urllib.urlencode(query_params))

class Guestlist(webapp2.RequestHandler):
    def get(self):
        rsvp_name = self.request.get('rsvp_name',
                                          DEFAULT_RSVP_NAME)
        rsvp_query = RSVPModel.query(
        ancestor=rsvp_key(rsvp_name)).order(-RSVPModel.date)
        rsvps = rsvp_query.fetch(30)

        template_values = {
            'rsvps': rsvps
        }

        template = JINJA_ENVIRONMENT.get_template('guestlist.html')
        self.response.write(template.render(template_values))

class Thanks(webapp2.RequestHandler):
    def get(self):
        rsvp = self.request.get("rsvp")

        template_values = {
            'rsvp': rsvp
        }

        template = JINJA_ENVIRONMENT.get_template('thanks.html')
        self.response.write(template.render(template_values))

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/invite', Invite),
    ('/rsvp', RSVP),
    ('/rsvp/guestlist', Guestlist),
    ('/thanks', Thanks),
], debug=True)
