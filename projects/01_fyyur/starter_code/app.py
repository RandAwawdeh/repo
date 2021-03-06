#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
#migrate = Migrate(app, db)

# TODO: connect to a local postgresql database Done

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120), nullable=False, unique=True)
    image_link = db.Column(db.String)
    facebook_link = db.Column(db.String)
    website = db.Column(db.String)
    genres = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='Venue')

    def __repr__(self):
      return f'<Venue {self.id}, {self.name}, {self.city}, {self.state}, {self.address}, {self.phone}, {self.image_link}, {self.facebook_link}, {self.website}, {self.genres}, {self.seeking_talent}, {self.seeking_description}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate Done

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False, unique=True)
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String)
    seeking_venue = db.Column(db.Boolean, nullable=False, default=True)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='Artist')

    def __repr__(self):
      return f'<Artist {self.id}, {self.name}, {self.city}, {self.state}, {self.phone}, {self.image_link}, {self.facebook_link}, {self.website}, {self.genres}, {self.seeking_venue}, {self.seeking_description}>'
      

    # TODO: implement any missing fields, as a database migration using Flask-Migrate Done

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration. Done
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)  
    
    #artist = db.relationship(Artist, backref=db.backref('shows', cascade='all, delete'))
    #venue = db.relationship(Venue, backref=db.backref('shows', cascade='all, delete'))
    def __repr__(self):
      return f'<Show {self.id}, {self.start_time},  {self.venue_id}, {self.artist_id}>'
      
db.create_all()


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data. Done
  #       num_shows should be aggregated based on number of upcoming shows per venue. Done

  areas = db.session.query(Venue.state, Venue.city, Venue.name, Venue.id).distinct(Venue.state, Venue.city)

  data = []

  for area in areas:

    areas = Venue.query.filter_by(state = area.state).filter_by(city = area.city).all()
    
    v_data=[]
    
    for venue in areas:
      v_data.append({
        'id': venue.id,
        'name':venue.name,
        'num_ucoming_shows': len(db.session.query(Show).all())
      })

    entry = {
      'city': area.city,
      'state' : area.state,
      'venues' : v_data,
    }
    data.append(entry)

  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.   DONE
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"  
  
  search_term = request.form.get('search_term','')
  
  venues = db.session.query(Venue).filter(Venue.name.ilike('%'+ search_term +'%')).all()
  
  data = []
  
  for venue in venues:
    num_upcoming_shows = 0
    shows = db.session.query(Show).filter(Show.venue_id == venue.id)
    for show in shows:
      if (Show.start_time > datetime.now()):
        num_upcoming_shows += 1
    
    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": num_upcoming_shows
    })

  response={
    "count": len(venues),
    "data": data
  }
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id Done
  # TODO: replace with real venue data from the venues table, using venue_id Done
  
  venue = db.session.query(Venue).filter(Venue.id == venue_id).one()
  
  show_list = db.session.query(Show).filter(Show.venue_id == venue_id)
  
  past_shows = []
  
  upcoming_shows = []

  for show in show_list:
    
    artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show.artist_id).one()
    
    show_add = {
        'artist_id': show.artist_id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': str(show.start_time)
        }
    if (show.start_time < datetime.now()):

        past_shows.append(show_add)

    else:
        upcoming_shows.append(show_add)

  data = {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
  }

  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  data = list(filter(lambda d: d['id'] == venue_id, [data]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead Done
  # TODO: modify data to be the data object returned from db insertion Done
  form = VenueForm(request.form)
  
  try:
    venue = Venue(
      name = request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      address = request.form.get('address'),
      phone = request.form.get('phone'),
      genres = request.form.getlist('genres'),
      image_link = request.form.get('image_link'),
      facebook_link = request.form.get('facebook_link'),
      website = request.form.get('website'),
      seeking_talent = True if 'seeking_talent' in request.form else False ,
      seeking_description = request.form.get('seeking_description')
      )
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except ValueError as e:
    db.session.rollback()
    flash('Error. Venue ' + 'Venue' + request.form['name'] + ' could not be listed ')
  finally:
    db.session.close()
  # on successful db insert, flash success DONE
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')  DONE
      
  # TODO: on unsuccessful db insert, flash an error instead. DONE
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.') DONE
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using  
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.  

  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('The venue has been deleted')

  except:
    db.session.rollback()
    flash('Unsuccessful deletion')

  finally:
    db.session.close()
  return None


  # try:
  #   venue = db.session.query(Venue).get(venue_id)
  #   db.session.delete(venue)
  #   db.session.commit()
  # except:
  #   db.session.rollback()
  #   flash('Unsuccessful deletion')
  # finally:
  #   db.session.close()
  # return None

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = db.session.query(Artist).all()
  
  # data=[
  #   {"id": 4,"name": "Guns N Petals",}, 
  #   {"id": 5,"name": "Matt Quevedo",}, 
  #   {"id": 6,"name": "The Wild Sax Band",}]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  search_term = request.form.get('search_term','')

  artists = db.session.query(Artist).filter(Artist.name.ilike('%'+ search_term +'%')).all()
  
  data = []
  
  for artist in artists:
    num_upcoming_shows = 0
    shows = db.session.query(Show).filter(Show.artist_id == artist.id)
    for show in shows:
      if (Show.start_time > datetime.now()):
        num_upcoming_shows += 1
    
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": num_upcoming_shows
    })

  response={
    "count": len(artists),
    "data": data
  }
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id

  artist = db.session.query(Artist).filter(Artist.id == artist_id).one()

  show_list = db.session.query(Show).filter(Show.artist_id == artist_id)

  past_shows = []

  upcoming_shows = []

  for show in show_list:
    
    venue = db.session.query(Venue.name, Venue.image_link).filter(Venue.id == show.venue_id).one()
    
    show_add = {
        'venue_id': show.venue_id,
        'venue_name': venue.name,
        'venue_image_link': venue.image_link,
        'start_time': str(show.start_time)
        }
    if (show.start_time < datetime.now()):

        past_shows.append(show_add)

    else:
        upcoming_shows.append(show_add)

  # artist = Artist.query.get(artist_id)

  # upcoming_shows = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).all()

  # past_shows = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id)

  # data_shows=[]

  # for upshow in upcoming_shows:
  #   upcoming_shows({
  #     'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
  #     })

  # for pshow in past_shows:
  #   past_show({
  #     'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
  #     })

  # TODO: replace with real venue data from the venues table, using venue_id
  
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  data = list(filter(lambda d: d['id'] == artist_id, [data]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  artist = Artist.query.filter_by(id=artist_id).first_or_404()
  form = ArtistForm(obj=artist)
  #artist={ "id": 4,
  # "name": "Guns N Petals",
  # "genres": ["Rock n Roll"],
  # "city": "San Francisco",
  # "state": "CA",
  # "phone": "326-123-5000",
  # "website": "https://www.gunsnpetalsband.com",
  # "facebook_link": "https://www.facebook.com/GunsNPetals",
  # "seeking_venue": True,
  # "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  # "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  #}
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm(request.form)

  try:
    artist = Artist.query.first_or_404(artist_id)
    form.populate_obj(artist)
    db.session.commit()
    flash(f'{form.name.data} edited seccessfully')

  except ValueError as e:
    db.session.rollback()
    flash('Error!')

  finally:
    db.session.close()


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  venue = Venue.query.first_or_404(venue_id)
  form = VenueForm(obj=venue)
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attribute

  form = VenueForm(request.form)

  try:
    venue = Venue.query.first_or_404(venue_id)
    form.populate_obj(venue)
    db.session.commit()
    flash(f'{form.name.data} edited seccessfully')

  except:
    db.session.rollback()
    flash('Error!')

  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form Done
  # TODO: insert form data as a new Venue record in the db, instead Done
  # TODO: modify data to be the data object returned from db insertion Done
  form = ArtistForm(request.form)

  try:
    artist = Artist(
      name = request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      phone = request.form.get('phone'),
      genres = request.form.getlist('genres'),
      image_link = request.form.get('image_link'),
      facebook_link = request.form.get('facebook_link'),
      website = request.form.get('website'),
      seeking_venue = True if 'seeking_venue' in request.form else False ,
      seeking_description = request.form.get('seeking_description')
    )
    db.session.add(artist)
    db.session.commit()
  # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except ValueError as e:
    db.session.rollback()
  # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  shows = db.session.query(Show.artist_id, Show.venue_id, Show.start_time).all()
  
  data = []

  for show in shows:
      
      artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show.artist_id).one()
      
      venue = db.session.query(Venue.name).filter(Venue.id == show.venue_id).one()
      
      data.append({
          "venue_id": show.venue_id,
          "venue_name": venue.name,
          "artist_id": show.artist_id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": str(show.start_time)
      })
    

  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  form = ShowForm(request.form)

  try:
    show = Show(
      artist_id = request.form.get("artist_id"),
      venue_id = request.form.get("venue_id"),
      start_time = request.form.get("start_time")
      )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except ValueError as e:
    db.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
