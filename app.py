import re
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_ngrok2 import run_with_ngrok
from flask_socketio import SocketIO

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'o_cheie_secretă_și_dificil_de_ghicit'
run_with_ngrok(app)
# Configurare MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'PythonPS'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)
bcrypt = Bcrypt(app)
socketio = SocketIO(app)

def hash_parola(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

@app.route('/')
def index():
    if 'UserID' not in session:
        return redirect(url_for('login'))

    user_id = session['UserID']
    cur = mysql.connection.cursor()

    # Fetch the username from the database based on the user_id
    cur.execute("SELECT name FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    username = user['name'] if user else 'Guest'

    # Fetch parking spots data
    cur.execute("SELECT * FROM parking_spots")
    parking_spots = cur.fetchall()

    # Fetch license numbers for reserved spots
    reserved_spot_ids = [spot['spot_id'] for spot in parking_spots if spot['is_reserved']]
    if reserved_spot_ids:
        cur.execute("SELECT reserved_by, license_number FROM parking_spots WHERE spot_id IN %s", (reserved_spot_ids,))
        license_numbers = {row['reserved_by']: row['license_number'] for row in cur.fetchall()}

        for spot in parking_spots:
            if spot['reserved_by'] in license_numbers:
                spot['license_number'] = license_numbers[spot['reserved_by']]
            else:
                spot['license_number'] = None  # Set to None if not found

    cur.close()
    
    return render_template('index.html', parking_spots=parking_spots, username=username)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        parola = request.form['psw']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and bcrypt.check_password_hash(user['password'], parola):
            session['UserID'] = user['id']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error_message='Email sau parolă incorectă.')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        psw = request.form['psw']
        license = request.form['license']
        cnp = request.form['cnp']

        email_error = None
        license_error = None
        cnp_error = None

        # Validarea CNP-ului
        cnp = request.form['cnp']
        cnp_pattern = re.compile(r'^(1|2|5|6)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])(0[1-9]|[1-4]\d|5[0-1])\d{3}[0-9]$')
        if not cnp_pattern.match(cnp):
            cnp_error = 'CNP-ul nu este valid.'

        # Validarea emailului
        if not email.endswith(('@gmail.com', '@yahoo.com')):
            email_error = 'Emailul trebuie să fie unul de tip @gmail.com sau @yahoo.com'

        # Validarea numărului de înmatriculare
        license_pattern = re.compile(r'^(AB|AG|AR|BC|BH|BN|BR|BT|BV|BZ|CJ|CL|CS|CT|CV|DB|DJ|GJ|GL|GR|HD|HR|IF|IL|IS|MH|MM|MS|NT|OT|PH|SB|SJ|SM|SV|TL|TM|TR|VL|VN|VS|B)\d{1,3}[A-Z]{3}$')
        if not license_pattern.match(license):
            license_error = 'Numărul de înmatriculare nu este valid.'

        if email_error or license_error or cnp_error:
            return render_template('register.html', email_error=email_error, license_error=license_error, cnp_error=cnp_error, name=name, email=email, license=license, cnp=cnp)

        hashed_password = hash_parola(psw)

        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO users (name, email, password, license_number, cnp) VALUES (%s, %s, %s, %s, %s)", 
                        (name, email, hashed_password, license, cnp))
            mysql.connection.commit()
        except Exception as e:
            flash('Eroare la înregistrare: ' + str(e), 'registration_error')
            return render_template('register.html', name=name, email=email, license=license, cnp=cnp)
        finally:
            cur.close()

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/reserve/<int:spot_id>')
def reserve(spot_id):
    user_id = session.get('UserID')
    if not user_id:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    # Check if the user already has a reserved parking spot
    cur.execute("SELECT * FROM parking_spots WHERE reserved_by = %s", (user_id,))
    if cur.fetchone():
        flash('Aveți deja un loc rezervat', 'error')  # Flash an error message
        cur.close()
        return redirect(url_for('index'))  # Redirect to the index page

    # Check if the requested spot is available
    cur.execute("SELECT * FROM parking_spots WHERE spot_id = %s AND is_reserved = False", (spot_id,))
    spot = cur.fetchone()

    if spot:
        # Get the user's license number from the database
        cur.execute("SELECT license_number FROM users WHERE id = %s", (user_id,))
        user_data = cur.fetchone()
        user_license_number = user_data['license_number']

        # Reserve the spot if it's available and update the license_number
        cur.execute("UPDATE parking_spots SET is_reserved = True, reserved_by = %s, license_number = %s WHERE spot_id = %s", (user_id, user_license_number, spot_id))
        mysql.connection.commit()

        # Emit the WebSocket event for real-time update
        socketio.emit('update_parking_spot', {'spot_id': spot_id, 'status': 'reserved', 'license_number': user_license_number})

    cur.close()

    return redirect(url_for('index'))



@app.route('/release', methods=['GET', 'POST'])
def release_spot():
    user_id = session.get('UserID')
    if not user_id:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    # Check if the user has a reserved parking spot
    cur.execute("SELECT * FROM parking_spots WHERE reserved_by = %s", (user_id,))
    reserved_spot = cur.fetchone()

    if not reserved_spot:
        # If no spot is reserved, flash a message and redirect
        flash('Nu aveți niciun loc rezervat', 'info')
        cur.close()
        return redirect(url_for('index'))  # Redirect to the index page

    spot_id = reserved_spot['spot_id']

    # Release the reserved parking spot
    cur.execute("UPDATE parking_spots SET is_reserved = False, reserved_by = NULL, license_number = NULL WHERE spot_id = %s", (spot_id,))
    mysql.connection.commit()

    # Emit the SocketIO event
    socketio.emit('spot_released', {'spot_id': spot_id, 'status': 'available'})

    cur.close()

    flash('Locul de parcare a fost eliberat', 'info')
    return redirect(url_for('index'))  # Redirect to the index page after releasing the spot


@app.route('/logout')
def logout():
    session.pop('UserID', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    socketio.run(app, debug=True)
