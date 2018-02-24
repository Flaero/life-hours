from flask import Flask, Markup, render_template, request
from datetime import datetime
import time
import pymysql


sanitize = str.maketrans('', '', """;:|{()}[]+=\*_"'""")

# Configuration
database_user = 'USER'
database_password = 'PASSWORD'
database_name = 'life_hours'
database_ip = 'localhost'


# Connect to mysql or mariadb server
db = pymysql.connect(database_ip, database_user, database_password, database_name)
c = db.cursor()


def report(description, hour):
	c.execute('SELECT * FROM hours WHERE hour='+str(hour))
	if len(c.fetchall()) > 0:
		return False
	else:
		c.execute('INSERT INTO hours(activity_description, hour) VALUES ("'+description+'",'+str(hour)+")")
		db.commit()
		return True

def getRecentHours(x): # Return the last x hours since the epoch
	current_hour = int(time.time()/60/60)
	recent_hours = []
	for i in range(x):
		recent_hours.append(current_hour-i)
	return recent_hours

def generateHTML(hours):
	html = ""
	for h in hours:
		hour = datetime.fromtimestamp(h*60*60).strftime('%d %H-') + datetime.fromtimestamp((h+1)*60*60).strftime('%H | ')
		c.execute("SELECT * FROM hours WHERE hour="+str(h))
		rows = c.fetchall()
		if len(rows):
			html += '<div class="timestep"><span>'+hour+'</span>'+rows[0][0]+'</div>'
		else:
			html += '<div class="empty">'+hour+'No entry<br><input type="text" name="'+str(h)+'"></div>'
	return Markup(html)


app = Flask(__name__)

@app.route("/", methods=['POST', 'GET'])
def index():
	status = "Life Hours"
	if request.method == 'GET':
		return render_template('index.html', status=status, rows=generateHTML(getRecentHours(48)))
	elif request.method == 'POST':
		for h in getRecentHours(49):
			activity = request.form.get(str(h))
			if activity and len(activity) > 2:
				if report(activity.translate(sanitize), h) == False:
					status = "ERROR: ATTEMPTED DUPLICATE ENTRY"

		return render_template('index.html', status=status, rows=generateHTML(getRecentHours(48)))


if __name__ == "__main__":
	c.execute('CREATE TABLE IF NOT EXISTS hours(activity_description TEXT, hour INT)')
	app.run(host='0.0.0.0', debug=True, port=8000, threaded=True)
	db.close()
