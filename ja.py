import logging
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
    date = ndb.DateTimeProperty(auto_now=True)
    email = ndb.StringProperty(indexed=False)
    firstName = ndb.StringProperty(indexed=True)
    group = ndb.IntegerProperty(indexed=True)
    lastName = ndb.StringProperty(indexed=True)
    message = ndb.StringProperty(indexed=False)
    rsvp = ndb.IntegerProperty(indexed=True)
    transportation = ndb.IntegerProperty(indexed=True)


class MainPage(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render())


class Invite(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('invite.html')
        self.response.write(template.render())


class RSVPAdd(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('rsvp_add.html')
        self.response.write(template.render())

    def post(self):
        rsvp_first_name = self.request.get('first_name').lower()
        rsvp_last_name = self.request.get('last_name').lower()
        rsvp_group = int(self.request.get('group'))

        rsvp = RSVPModel()
        rsvp.firstName = rsvp_first_name
        rsvp.lastName = rsvp_last_name
        rsvp.group = rsvp_group

        rsvp.put()

        template = JINJA_ENVIRONMENT.get_template('rsvp_add.html')
        self.response.write(template.render())


class RSVPFind(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('rsvp_find.html')
        self.response.write(template.render())

    def post(self):
        rsvp_first_name = self.request.get('first_name').lower()
        rsvp_last_name = self.request.get('last_name').lower()

        query = RSVPModel.query(
            RSVPModel.firstName == rsvp_first_name,
            RSVPModel.lastName == rsvp_last_name
        )

        result = query.get()

        if result is None:
            logging.error(
                rsvp_first_name + ' ' + rsvp_last_name + ' was not found'
            )
            template_values = {
                'error': 'NOT_FOUND',
                'message': 'Name not found, please try again or try another name in your party'
            }
            template = JINJA_ENVIRONMENT.get_template('rsvp_find.html')
            self.response.write(template.render(template_values))
        else:
            query_params = {'group': result.group}
            self.redirect('/rsvp/found?' + urllib.urlencode(query_params))


class RSVP(webapp2.RequestHandler):

    def get(self):
        rsvp_group = int(self.request.get('group'))

        rsvp_query = RSVPModel.query(RSVPModel.group == rsvp_group)

        rsvps = rsvp_query.fetch()

        template_values = {
            'rsvps': rsvps,
            'group': rsvp_group
        }

        template = JINJA_ENVIRONMENT.get_template('rsvp.html')
        self.response.write(template.render(template_values))

    def post(self):
        rsvp_yes = 0

        rsvp_group = int(self.request.get('group'))

        rsvp_query = RSVPModel.query(RSVPModel.group == rsvp_group)

        rsvps = rsvp_query.fetch()

        for rsvp in rsvps:
            rsvp.rsvp = int(self.request.get('rsvp_'+rsvp.firstName))
            if rsvp.rsvp and rsvp_yes == 0:
                rsvp_yes = 1
            else:
                rsvp_yes = 2

            rsvp.email = self.request.get('email')
            if self.request.get('transportation'):
                rsvp.transportation = 1
            else:
                rsvp.transportation = 0
            rsvp.message = self.request.get('message')
            rsvp.put()

        query_params = {'rsvp': rsvp_yes}
        self.redirect('/thanks?' + urllib.urlencode(query_params))


class Guestlist(webapp2.RequestHandler):
    def get(self):
        rsvp_query = RSVPModel.query().order(RSVPModel.group)
        rsvps = rsvp_query.fetch(250)

        rsvp_query_yes = RSVPModel.query(RSVPModel.rsvp == 1)
        rsvps_yes = rsvp_query_yes.fetch(250)

        rsvp_query_no = RSVPModel.query(RSVPModel.rsvp == 0)
        rsvps_no = rsvp_query_no.fetch(250)

	rsvp_query_none = RSVPModel.query(RSVPModel.rsvp == None)
	rsvps_none = rsvp_query_none.fetch(250)

	rsvp_query_transportation = RSVPModel.query(RSVPModel.transportation == 1)
	rsvps_transportation = rsvp_query_transportation.fetch(250)

	rsvp_none = len(rsvps)-len(rsvps_yes)-len(rsvps_no)

        template_values = {
            'rsvps': rsvps,
            'total': len(rsvps),
            'yes': len(rsvps_yes),
            'no': len(rsvps_no),
	    'rsvps_none': len(rsvps_none),
	    'transportation': len(rsvps_transportation)
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
    ('/rsvp', RSVPFind),
    ('/rsvp/found', RSVP),
    ('/rsvp/guestlist', Guestlist),
    ('/rsvp/add', RSVPAdd),
    ('/thanks', Thanks),
], debug=True)
