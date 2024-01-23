from flask import(
    Flask,
    flash,
    request,
    render_template,
    redirect,
    session,
    url_for,
    jsonify,
    send_file
)
from app.dao import Dao
from app.business import Business
import hashlib
from datetime import datetime
import matplotlib

app=Flask(__name__)
def generateKey(login):
   return hashlib.sha512(str(login).encode('utf-8')).hexdigest()
daoo=Dao()
services = Business()
app.secret_key='1234'
matplotlib.use('Agg')
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
        id=daoo.getMaxId()
        name=request.form['name']
        address=request.form['address']
        type=request.form['type']
        
        daoo.addClient({'id':id+1,'name':name, 'address':address, 'type':type})
        
        return render_template('client_details.html', client_list=daoo.getClients())
    else:
        return render_template('client_details.html', error_add='Client not added for some reason !', client_list=daoo.getClients())
        
@app.route('/details', methods=['post'])  
def details():
    client_id = request.form.get('client_id')
    print(client_id)
    if client_id:
        client=daoo.selectClient(client_id)
        print(client)
        if client["type"] == 'ENDDEVICE':
            daoo.currentED=client["id"]
            data = daoo.getEndDevices(client["id"])
            #print("data : ", data)
            chart_paths = services.create_dashboard_enddevice(data)
            #print("charts : ", chart_paths)
            return render_template('dashboardEndDevice.html', chart_paths=chart_paths)
            
        elif client["type"] == "CITY":
            daoo.currentCity = client["name"]
            data1, data2, dates1, dates2 = services.create_dashboard_city(client["name"], "2024-01-01", "2024-01-10")
            #data_dict = services.get_precipitation_history_openweather(client["name"], "2024-01-01", "2024-01-02")
            return render_template('dashboardCity.html', precipitation_data=data1, predictions_data=data2, date_labels=dates1, date_labels2=dates2)
        elif client["type"] == "IOT":
            daoo.currentIOT = client["address"]
            data = daoo.getIOTDataByMac(client["address"])
            chart_path=services.create_dashboard_IOT(data)
            return render_template('dashboardIOT.html', chart_path=chart_path)
        else:
            flash("Unsupported client type")
    return render_template('client_details.html', client_list=daoo.getClients())

@app.route('/charts/<chart_name>')
def serve_chart(chart_name):
    return send_file(chart_name, mimetype='image/png')

@app.route('/deleteClient', methods=['POST'])
def deleteClient():
    client_id = request.form.get('client_id')
    if client_id:
        daoo.delete(client_id)
    return render_template('client_details.html', client_list=daoo.getClients())

@app.route('/logout')
def logout():
    session.pop('user_id',None)
    return redirect(url_for('index'))

@app.route('/dashboardCity')
def dashboard():
    return render_template('dashboard.html')

@app.route('/update_charts', methods=['POST'])
def update_charts():
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    data1, data2, dates1, dates2 = services.create_dashboard_city(daoo.currentCity, start_date, end_date)
    #data_dict = services.get_precipitation_history_openweather(client["name"], "2024-01-01", "2024-01-02")
    return render_template('dashboardCity.html', precipitation_data=data1, predictions_data=data2, date_labels=dates1, date_labels2=dates2)
@app.route('/update_charts_end_device', methods=['POST'])
def update_charts_end_device():
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    data = daoo.getEndDevicesByDate(daoo.currentED, start_date, end_date)
    print("data : ", data)
    chart_paths = services.create_dashboard_enddevice(data)
    print("charts : ", chart_paths)
    return render_template('dashboardEndDevice.html', chart_paths=chart_paths)
@app.route('/update_charts_iot', methods=['POST'])
def update_charts_iot():
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    data = daoo.getIOTByMacAndDate(daoo.currentIOT, start_date, end_date)
    chart_path=services.create_dashboard_IOT(data)
    return render_template('dashboardIOT.html', chart_path=chart_path)