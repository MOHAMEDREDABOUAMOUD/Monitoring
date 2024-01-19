from flask import(
    Flask,
    flash,
    request,
    render_template,
    redirect,
    session,
    url_for,
    jsonify
)
from app.dao import dao
from app.business import Business
import hashlib
from datetime import datetime

app=Flask(__name__)
def generateKey(login):
   return hashlib.sha512(str(login).encode('utf-8')).hexdigest()
daoo=dao()
services = Business()
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
def details():
    client_id = request.form.get('client_id')
    if client_id:
        client=daoo.selectClient(client_id)
        if client["type"] == 'ENDPOINT':
            # stats = daoo.getstats(client["address"], "public")
            # print(stats)
            ip_target='127.0.0.1'
            community='public'
            memory_ram_oid='.1.3.6.1.2.1.25.2.2.0'
            memory_used_oid='.1.3.6.1.2.1.25.2.3.1.6.1'
            memory_total_oid='.1.3.6.1.2.1.25.3.6.1.4.45'
            print('total ROM : ',services.get_disk_storage_info(ip_target,community)[0])
            print('used ROM : ',services.get_disk_storage_info(ip_target,community)[1])
            #print('total RAM : ',services.get(ip_target,community,memory_ram_oid))
            print('total RAM : ',services.get_disk_storage_info(ip_target, community)[2])
            print("Used RAM : ",services.get_disk_storage_info(ip_target,community)[3])
            # print('charge cpu : ',services.get(ip_target,community,cpu_oid))
            # print('some cpu : ', services.get_sum_of_cpu_cores(ip_target,community))
            # print('max cpu ghz : ', services.get_max_clock_speed())
            print('charge cpu : ', services.get_cpu_percentage(ip_target,community))
            
        elif client["type"] == "CITY":
            data_dict = services.get_precipitation_history_openweather(client["name"], "2024-01-01", "2024-01-02")
            for date, data in data_dict.items():
                print(f"Weather on {date} in {client["name"]}:")
                for key, value in data.items():
                    print(f"{key}: {value}")
                print("\n")
            return render_template('dashboardCity.html', data_dict=data_dict)
        else:
            flash("Unsupported client type")
    return render_template('client_details.html', client_list=daoo.getClients())

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
def update_charts_route():
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    print(daoo.currentCity, start_date, end_date)
    data_dict = services.get_precipitation_history_openweather(daoo.currentCity, start_date, end_date)
    return render_template('dashboardCity.html', data_dict=data_dict)