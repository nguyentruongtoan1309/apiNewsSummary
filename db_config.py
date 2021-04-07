from app import app
from flaskext.mysql import MySQL
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Nguyentro1309#1'
app.config['MYSQL_DATABASE_DB'] = 'you_news'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['JSON_AS_ASCII'] = False

mysql.init_app(app)
