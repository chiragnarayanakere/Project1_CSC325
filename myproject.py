import os
from flask import Flask
from flask import render_template, redirect, url_for, json, make_response, request,session
from flask_sqlalchemy import SQLAlchemy

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "userlogs.db"))

app = Flask(__name__)
app.secret_key = 'a secret key to rule them all'
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True;
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True;

db = SQLAlchemy(app)

@app.route("/")
def root():
	session.permanent = True
	
	if('uid' in session):
		uid = session['uid']
	else:
		uid = None

	user_agent = request.headers.get('User-Agent', None)  # get the user agent
	current_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr) # get the user_ip
	referrer = request.referrer or None  # get the referrer page

	if(uid is not None):
		db_u = User.query.get(uid)
	else:
		db_u = None

	try:
		if(db_u is not None):
			db_u.user_agent = user_agent
			db_u.last_ip = current_ip
			db_u.visit_count += 1
			db.session.commit()
			session['uid'] = db_u.user_id
		else:
			u = User(user_agent, current_ip, referrer)
			db.session.add(u)
			db.session.commit()
			session['uid'] = u.user_id
	except Exception as e:
		print("Failed to add User")
		print(e)

	return render_template('index.html')

@app.route("/userlogs")
def logs():
	return render_template('userlogs.html', users=User.query.all())
# logs

class User(db.Model):
	user_id = db.Column('user_id', db.Integer, primary_key = True)
	user_agent = db.Column('user_agent', db.String(80),nullable=True)
	last_ip = db.Column('last_ip', db.String(80),nullable=True)
	referrer = db.Column('referrer', db.String(80),nullable=True)
	visit_count =  db.Column('visit_count', db.Integer)

	def __init__(self, user_agent, ip, referrer):
		self.last_ip  = ip
		self.user_agent = user_agent
		self.referrer = referrer
		self.visit_count = 0

	def __repr__(self):
		return "id: {}>".format(self.user_id)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
