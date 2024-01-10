from flask import(
    Flask,
    request,
    render_template,
    redirect,
    session,
    url_for,
    jsonify
)
from app.dao import dao
import hashlib
from datetime import datetime

app=Flask(__name__)
def generateKey(login):
   return hashlib.sha512(str(login).encode('utf-8')).hexdigest()
daoo=dao()
app.secret_key='1234'
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        login=request.form['username']
        pwd=request.form['password']
        
        if daoo.Authentificate(login=login,password=pwd):
            app.secret_key=generateKey(login)
            response=app.make_response(render_template('client_details.html', client_list=daoo.getClients()))
            session["user_id"]=login
            response.set_cookie('access_time',str(datetime.now()))
            #access_time=request.cookies.get('access_time')
            return response
        else:
            return render_template('login.html',error_auth="login or password incorrect")
    return render_template('login.html')
@app.route('/create_client', methods=['POST'])
def create_client():
    if request.method == 'POST':
        name=request.form['name']
        address=request.form['address']
        type=request.form['type']
        latitude=request.form['latitude']
        longitude=request.form['longitude']
        
        daoo.addClient({'name':name, 'address':address, 'type':type, 'latitude':latitude, 'longitude':longitude})
        
        return render_template('client_details.html', client_list=daoo.getClients())
    else:
        return render_template('client_details.html', error_add='Client not added for some reason !', client_list=daoo.getClients())
        
@app.route('/details', methods=['post'])  
def details(client_id):
        return render_template('client_details.html', client_list=daoo.getClients())
@app.route('/logout')
def logout():
    session.pop('user_id',None)
    return redirect(url_for('index'))