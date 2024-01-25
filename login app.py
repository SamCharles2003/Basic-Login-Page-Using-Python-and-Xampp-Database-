from flask import Flask,render_template,jsonify,request,redirect,url_for,session
import pymysql
import time
import email
import smtplib
import threading
from datetime import datetime, timedelta , timezone
import random
import os
import binascii
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app=Flask(__name__)

conn = pymysql.connect(host='localhost', user='root', password='',database='login_users')
cursor = conn.cursor()

secret_key = binascii.hexlify(os.urandom(24)).decode('utf-8')
app.secret_key = secret_key

@app.route(rule='/',methods=['GET'])
def admin_check():
    return render_template(template_name_or_list='admin_login.html')


@app.route(rule='/check_user', methods=['POST','GET'])
def check_user():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor.execute('SELECT * FROM users WHERE email = % s AND password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['email'] = email
            mesage = 'Logged in successfully !'
            return  redirect(url_for('teacher'))
        else:
            mesage = 'Please enter correct email / password !'
            return render_template('admin_login.html', mesage = mesage)


@app.route(rule='/forgot_password',methods=['GET'])
def forgot_password():
    return render_template(template_name_or_list='forgot_password.html')

@app.route(rule='/change_password', methods=['POST'])
def change_password():
    try:

        data = request.json
        email= data.get('email')
        cursor.execute( f"SELECT * FROM `users` WHERE `email` = '{email}'")
        count = cursor.fetchone()
        if count:
            otp = generate_otp()
            session['otp_data'] = {'otp': otp, 'timestamp': datetime.now()}
            session['email'] = email
            session['forget_email'] = email
            email_thread = threading.Thread(target=send_otp_email, args=(email, otp))
            email_thread.start()
            return jsonify({'message': 'success'})


        else:
            return jsonify({ 'message': 'Account was not Found!'})
    except Exception as e:
        return jsonify({'message': 'error', 'error': str(e)})


@app.route(rule='/otp_verification',methods=['GET'])
def otp_verification():
    return render_template(template_name_or_list='otp_verification.html')


@app.route(rule='/verify_otp', methods=['POST'])
def verify_otp():
    print("control Here")
    entered_otp = request.json.get('otp')
    print("Entered OTP",entered_otp)
    print ('otp_data' in session )
    if 'otp_data' in session and 'email' in session:
        print("otp data")
        if not is_otp_session_expired(session['otp_data']['timestamp']):
            stored_otp = session['otp_data']['otp']
            if entered_otp == stored_otp:
                return jsonify({'message': 'success'})
            else:
                return jsonify({'message': 'error'})
    else:
        return jsonify({'message':'timeout'})

    # Add a default return statement in case the conditions are not met


@app.route(rule='/timeout',methods=['GET'])
def timeout():
    return render_template(template_name_or_list='session_closed.html')


@app.route(rule='/update_password',methods=['GET'])
def update_password():
    return render_template(template_name_or_list='change_password.html')


@app.route(rule='/update_password_data', methods=['POST'])
def update_password_data():
    try:
        data = request.json
        email=session['forget_email']
        new_password = data.get('confirmpassword')
        print("UPDATE_PASSWORD_DATA() EMAIL---->",email)
        # Check if the email exists in the database
        cursor.execute(f"SELECT COUNT(*) FROM users WHERE email = '{email}'")
        count = cursor.fetchone()[0]

        if count > 0:
            # Update the password for the given email
            cursor.execute(f"UPDATE users SET password = '{new_password}' WHERE email = '{email}'")
            conn.commit()
            confirmation_email_thread = threading.Thread(target=confirmation_email, args=(email,))
            confirmation_email_thread.start()
            return jsonify({'message': 'success'})

        else:

            return  jsonify({'message': 'error', 'error': 'Email not found in the database'})


    except Exception as e:
        print("UPDATE_PASSWORD_DATA()---->ERROR:", e)
        return jsonify({'message': 'error', 'error': str(e)})


def confirmation_email(email):
    try:
        # Fetch email id from the database based on the provided email
        cursor.execute(f"SELECT email FROM users WHERE email = '{email}'")
        recipient_email = cursor.fetchone()[0]

        # Email configuration (update with your SMTP server details)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_username = "" ## Your SMTP mail
        smtp_password = "" ##Your SMTP Password

        # Sender and recipient email addresses
        sender_email = "" ## your Sender mail

        # Create a MIME object to represent the email
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient_email
        message['Subject'] = "Password Change Confirmation"

        # Construct the email body
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        email_body = f"Dear User,\n\nYour password for the account {email} was changed at {current_time}.\n\nThis change is confirmed.\n\nBest regards,\nYour App Team"

        # Attach the email body to the MIME object
        message.attach(MIMEText(email_body, 'plain'))

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, recipient_email, message.as_string())

        print("Confirmation Email sent successfully.")

    except Exception as e:
        print(f"Error sending email: {e}")


def generate_otp():
    return str(random.randint(100000, 999999))


def is_otp_session_expired(timestamp):
    # Make the current time offset-aware
    current_time = datetime.now(timezone.utc)
    # Ensure that the timestamp is offset-aware
    if timestamp.tzinfo is None or timestamp.tzinfo.utcoffset(timestamp) is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return current_time > timestamp + timedelta(minutes=10)


def send_otp_email(email,otp):
    try:
        # Fetch email id from the database based on the provided rfid_tag
        cursor.execute(f"SELECT email FROM users WHERE email = '{email}'")
        recipient_email = cursor.fetchone()[0]
        # Email configuration (update with your SMTP server details)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_username = "" ## Your Smtp mail
        smtp_password = "" ## Your Smtp Password

        # Sender and recipient email addresses
        sender_email = "" ## Your Sender mail

        # Create a MIME object to represent the email
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient_email
        message['Subject'] = "One Time Password for Account Recovery"

        # Construct the email body
        email_body = f"Dear User,\n\nYour One Time Password for the account {email} is: {otp}\n\nThis OTP is valid for 10 Minutes\nYour App Team"

        # Attach the email body to the MIME object
        message.attach(MIMEText(email_body, 'plain'))

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        print("Email Sent Successfully")
        return 1

    except Exception as e:
        print(f"Error sending email: {e}")


@app.route(rule='/sign_up',methods=['GET'])
def sign_up():
    return render_template('sign_up.html')


from flask import jsonify


@app.route(rule='/signupdata', methods=['POST'])
def signupdata():
    try:
        data = request.json
        name = data.get('firstName')
        email = data.get('email')
        password = data.get('password')
        phoneNumber = data.get('phoneNumber')
        otp=data.get('otp')
        print("SIGNUPDATA()--->Entered name", name)
        print("SIGNUPDATA()--->Entered email", email)
        print("SIGNUPDATA()--->Entered Password", password)
        print("SIGNUPDATA()--->Entered Phone number", phoneNumber)
        print("SIGNUPDATA()--->Entered OTP", otp)
        print('SIGNUPDATA()--->otp_data' in session)
        if 'otp_data' in session and 'email' in session:
            print("otp data")
            if not is_otp_session_expired(session['otp_data']['timestamp']):
                stored_otp = session['otp_data']['otp']
                print("SIGNUPDATA()--->Stored OTP", stored_otp)
                if otp == stored_otp:
                    cursor.execute(
                        "INSERT INTO users (Username, email, password, phone_number) VALUES (%s, %s, %s, %s)",
                        (name, email, password, phoneNumber))
                    conn.commit()
                    return jsonify({'message': 'success'})
                else:
                    return jsonify({'message': 'error'})
            else:
                return render_template(template_name_or_list='session_closed.html')
        else:
            return jsonify({'message': 'timeout'})

    except Exception as e:
        return jsonify({'message': 'error', 'error': str(e)})


@app.route(rule='/logout',methods=['GET'])
def logout():
    session['loggedin'] = False
    session['email'] = ""
    print("Successfully Looged Outx`")
    return render_template(template_name_or_list='admin_login.html')


@app.route(rule='/signup_otp', methods=['POST'])
def signup_otp():
    try:
        print("Control in signup_otp")
        data = request.json
        email = data.get('email')

        # Check if the email already exists in the database
        cursor.execute("SELECT * FROM `users` WHERE `email` = %s", args=(email,))
        existence = cursor.fetchall()

        if not existence:
            otp = generate_otp()
            session['otp_data'] = {'otp': otp, 'timestamp': datetime.now()}
            session['email'] = email
            email_thread = threading.Thread(target=signup_send_otp_email, args=(email, otp))
            email_thread.start()
            return jsonify({'message': 'success'})
        else:
            return jsonify({'message': "This User is Already Taken!"})

    except Exception as e:
        print("SIGNUP_OTP----> Error:", e)
        return jsonify({'message': 'error'})


def signup_send_otp_email(email,otp):
    try:
        recipient_email=email
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_username = "" ## your SMTP Username
        smtp_password = "" ## your Smtp password

        # Sender and recipient email addresses
        sender_email = "" ## Your Sender mail

        # Create a MIME object to represent the email
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient_email
        message['Subject'] = "One Time Password for SignUp Account"

        # Construct the email body
        email_body = f"Dear User,\n\nYour One Time Password for the account {email} is: {otp}\n\nThis OTP is valid for 10 Minutes\nSam Charles's App "

        # Attach the email body to the MIME object
        message.attach(MIMEText(email_body, 'plain'))

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        print("Email Sent Successfully")
        return 1

    except Exception as e:
        print(f"Error sending email: {e}")

###################################################################
def internal_1_list():
    try:
        cursor.execute("SELECT `Name`, `Tamil`, `English`, `Maths`, `Science`, `Social`, `Total` FROM `internal_1` ")
        rows = cursor.fetchall()
        
        # Make sure the index used to access columns matches the order in your SQL query
        dict_list = [{'Name': row[0], 'Tamil': row[1], 'English': row[2], 'Maths': row[3], 'Science': row[4], 'Social': row[5], 'Total': row[6]} for row in rows]
        
        return dict_list
    except Exception as e:
        print("ERROR:", e)
        
def today_attendance():
    try:
        cursor.execute("SELECT `Name`, `Status` FROM `attendance` ")
        rows = cursor.fetchall()
        dict_list = [{'Name': row[0], 'Status': row[1]} for row in rows]
        return dict_list
    except Exception as e:
        print("ERROR:",e)
         
              
@app.route(rule='/teacher',methods=['GET'])
def teacher():
    attendance=today_attendance()
    email=session['email']
    return render_template(template_name_or_list='success.html',attendance=attendance,email=email)
            
            
@app.route(rule='/internal_1',methods=['GET'])
def it_1():
    internal_1=internal_1_list()
    email=session['email']
    return render_template(template_name_or_list='internal_1.html',internal_1=internal_1,email=email)

@app.route(rule='/about',methods=['GET'])
def about():
    email=session['email']
    return render_template(template_name_or_list='about.html',email=email)

@app.route(rule='/contact',methods=['GET'])
def contact():
    email=session['email']
    return render_template(template_name_or_list='contacts.html',email=email)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9900,debug=True)
