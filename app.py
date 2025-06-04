from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from flask_session import Session
from werkzeug.utils import secure_filename
from modules.config import FAHRZEUGE, WEITERE_KRAEFTE, font_Headline_path, font_Einsatzstichwort_path, ROOM_CALENDAR, DROHNE_CALENDAR, FOOTER_TEXT
from modules.image_processing import allowed_file, correct_image_orientation, add_watermark
from modules.social_media import generate_social_media_post
from modules.calendar import add_event_to_calendar
from modules.google_calendar import add_event_to_google_calendar
from openai import OpenAI
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import os
import logging
import base64
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/var/www/feuerwehr-webapp/static/uploads'
app.config['STATIC_FOLDER'] = '/var/www/feuerwehr-webapp/static'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['ROOM_CALENDAR'] = ROOM_CALENDAR
app.config['DROHNE_CALENDAR'] = DROHNE_CALENDAR
app.secret_key = 'supersecretkey'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = '/var/www/feuerwehr-webapp/flask_session'
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///checkliste.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Session(app)

db = SQLAlchemy(app)

#TODO: Setze hier die jeweiligen bereichs Passwörter
passwords = {
    'social_media': 'yourpassword',
    'raumbuchung': 'yourpassword',
    'drohnenbuchung': 'yourpassword',
    'drohnen_checkliste': 'yourpassword',
    'hydrantenpflege': 'yourpassword'
}

os.makedirs(app.config['STATIC_FOLDER'], exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

client = OpenAI(api_key=app.config.get('OPENAI_API_KEY'))

logging.basicConfig(filename='/var/www/feuerwehr-webapp/app.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

class DrohnenCheckliste(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    startplatz_eingerichtet = db.Column(db.Boolean, default=False)
    fernsteuerung_einschalten = db.Column(db.Boolean, default=False)
    bildschirm_schaltet_ein = db.Column(db.Boolean, default=False)
    rotoren_ueberpruefen = db.Column(db.Boolean, default=False)
    drohne_einschalten = db.Column(db.Boolean, default=False)
    app_startet = db.Column(db.Boolean, default=False)
    kompass_kalibrieren = db.Column(db.Boolean, default=False)
    keine_warnungen = db.Column(db.Boolean, default=False)
    gps_empfang = db.Column(db.Boolean, default=False)
    verbindung_voller_ausschlag = db.Column(db.Boolean, default=False)
    akkuladezustand = db.Column(db.Boolean, default=False)
    flugmodus_p = db.Column(db.Boolean, default=False)
    startplatz_fest = db.Column(db.Boolean, default=False)
    automatischen_start_einleiten = db.Column(db.Boolean, default=False)
    aufsteigen = db.Column(db.Boolean, default=False)
    keine_warnmeldungen = db.Column(db.Boolean, default=False)
    homepoint_gesetzt = db.Column(db.Boolean, default=False)
    schwebeflug = db.Column(db.Boolean, default=False)
    drehen_360 = db.Column(db.Boolean, default=False)
    gieren = db.Column(db.Boolean, default=False)
    sinkflug = db.Column(db.Boolean, default=False)
    akkustand_flugziel = db.Column(db.Boolean, default=False)
    anflug_landezone_frei = db.Column(db.Boolean, default=False)
    landezone_frei = db.Column(db.Boolean, default=False)
    landezone_anfliegen = db.Column(db.Boolean, default=False)
    kamera_herunterschwenken = db.Column(db.Boolean, default=False)
    drohne_abwenden = db.Column(db.Boolean, default=False)
    sinken_landegeschwindigkeit = db.Column(db.Boolean, default=False)
    motoren_abschalten = db.Column(db.Boolean, default=False)
    ort = db.Column(db.String(100), nullable=False)
    datum = db.Column(db.Date, nullable=False)
    unterschrift = db.Column(db.String(100), nullable=False)

class Hydrant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nummer = db.Column(db.String(50), unique=True, nullable=False)
    standortbeschreibung = db.Column(db.String(255), nullable=False)
    utm_koordinate = db.Column(db.String(100), nullable=True)
    gps_daten = db.Column(db.String(100), nullable=True)

class HydrantData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hydrant_id = db.Column(db.Integer, db.ForeignKey('hydrant.id'), nullable=False)
    datum = db.Column(db.Date, nullable=False)
    bemerkung = db.Column(db.Text, nullable=True)
    wert_1 = db.Column(db.Integer, nullable=True)
    wert_2 = db.Column(db.Integer, nullable=True)
    wert_3 = db.Column(db.Integer, nullable=True)
    wert_4 = db.Column(db.Integer, nullable=True)
    hydrant = db.relationship('Hydrant', backref=db.backref('entries', lazy=True))

# Initialisieren Sie die Datenbank
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET'])
def start():
    return render_template('start.html', footer_text=FOOTER_TEXT)

@app.route('/password_check', methods=['POST'])
def password_check():
    if request.content_type == 'application/json':
        data = request.get_json()
        password = data.get('password')
        page = data.get('page')
        
        if password == passwords.get(page):
            session[page + '_authenticated'] = True
            return jsonify({'success': True})
        else:
            return jsonify({'success': False})
    else:
        password = request.form.get('password')
        page = request.form.get('page')
        
        if password == passwords.get(page):
            session[page + '_authenticated'] = True
            return redirect(url_for(page))
        else:
            return render_template('start.html', message='Falsches Passwort für diesen Bereich')


@app.route('/social_media', methods=['GET', 'POST'])
def social_media():
    is_authenticated = session.get('social_media_authenticated', False)
    if not is_authenticated:
        return render_template('social_media.html', is_authenticated=is_authenticated)

    if request.method == 'POST':
        try:
            # Einsatzdaten verarbeiten
            einsatznummer = request.form['einsatznummer']
            einsatzstichwort = request.form['einsatzstichwort']
            einsatzmeldung = request.form['einsatzmeldung']
            uhrzeit = request.form['uhrzeit']
            datum = request.form['datum']
            ort = request.form['ort']
            einsatzbericht = request.form['einsatzbericht']
            use_gpt = request.form.get('usegpt')
            fahrzeuge = request.form.getlist('fahrzeuge')
            weitere_kraefte = request.form.getlist('weitere_kraefte')

            # Fahrzeuge und weitere Kräfte als Text formatieren
            fahrzeuge_text = '\n'.join(fahrzeuge)
            weitere_kraefte_text = '\n'.join(weitere_kraefte)


            # Generiere den Social-Media-Post
            post_text = generate_social_media_post(
                einsatznummer, einsatzstichwort, einsatzmeldung, uhrzeit, datum, ort, einsatzbericht, fahrzeuge_text, weitere_kraefte_text, client, use_gpt
            )

            logging.debug("Generated post text successfully")

            # Erfolgsantwort mit dem generierten Post
            return jsonify({'success': True, 'post_text': post_text})

        except Exception as e:
            logging.error(f"Error occurred: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    # Wenn es sich um eine GET-Anfrage handelt, stelle sicher, dass der Benutzer authentifiziert ist
    predefined_images = os.listdir(os.path.join(app.config['STATIC_FOLDER'], 'predefined'))
    return render_template('social_media.html', predefined_images=predefined_images, fahrzeuge_list=FAHRZEUGE, weitere_kraefte_list=WEITERE_KRAEFTE, footer_text=FOOTER_TEXT, is_authenticated=is_authenticated)



@app.route('/raumbuchung', methods=['GET', 'POST'])
def raumbuchung():
    is_authenticated = session.get('raumbuchung_authenticated', False)
    if not is_authenticated:
        return render_template('raumbuchung.html', is_authenticated=is_authenticated, footer_text=FOOTER_TEXT)

    if request.method == 'POST':
        booker = request.form['booker']
        start = request.form['start']
        end = request.form['end']
        object = 'Raum'
        
        if not start or not end:
            return "Start- und Endzeit müssen angegeben werden.", 400
        
        start_dt = datetime.strptime(start, '%Y-%m-%dT%H:%M')
        end_dt = datetime.strptime(end, '%Y-%m-%dT%H:%M')
        
        if start_dt >= end_dt:
            return "Endzeit muss nach der Startzeit liegen.", 400

        link, error = add_event_to_google_calendar(app.config['ROOM_CALENDAR'], booker, start_dt, end_dt, multi_day=True)
        
        if error:
            error_message =  f"Fehler bei der Raumbuchung: {error}"
            return render_template('result_calendar.html', error_message=error_message, footer_text=FOOTER_TEXT, is_authenticated=is_authenticated)
        return render_template('result_calendar.html', object=object, booker=booker, start=start_dt, end=end_dt, footer_text=FOOTER_TEXT)
    return render_template('raumbuchung.html', footer_text=FOOTER_TEXT, is_authenticated=is_authenticated)

@app.route('/drohnenbuchung', methods=['GET', 'POST'])
def drohnenbuchung():
    is_authenticated = session.get('drohnenbuchung_authenticated', False)
    if not is_authenticated:
        return render_template('drohnenbuchung.html', is_authenticated=is_authenticated)
    
    if request.method == 'POST':
        booker = request.form['booker']
        start = request.form['start']
        end = request.form['end']
        object = 'Drohne'
        
        if not start or not end:
            return "Start- und Endzeit müssen angegeben werden.", 400

        start_dt = datetime.strptime(start, '%Y-%m-%dT%H:%M')
        end_dt = datetime.strptime(end, '%Y-%m-%dT%H:%M')
        
        if start_dt >= end_dt:
            return "Endzeit muss nach der Startzeit liegen.", 400

        link, error = add_event_to_google_calendar(app.config['DROHNE_CALENDAR'], booker, start_dt, end_dt)
        
        if error:
            error_message = f"Fehler bei der Drohnenbuchung: {error}"
            return render_template('result_calendar.html', error_message=error_message, footer_text=FOOTER_TEXT, is_authenticated=is_authenticated)
        return render_template('result_calendar.html', object=object, booker=booker, start=start_dt, end=end_dt, footer_text=FOOTER_TEXT)
    return render_template('drohnenbuchung.html', footer_text=FOOTER_TEXT, is_authenticated=is_authenticated)

@app.route('/drohnen_checkliste', methods=['GET', 'POST'])
def drohnen_checkliste():
    is_authenticated = session.get('drohnen_checkliste_authenticated', False)
    if not is_authenticated:
        return render_template('drohnen_checkliste.html', is_authenticated=is_authenticated, footer_text=FOOTER_TEXT)

    if request.method == 'POST':
        startplatz_eingerichtet = 'startplatz_eingerichtet' in request.form
        fernsteuerung_einschalten = 'fernsteuerung_einschalten' in request.form
        bildschirm_schaltet_ein = 'bildschirm_schaltet_ein' in request.form
        rotoren_ueberpruefen = 'rotoren_ueberpruefen' in request.form
        drohne_einschalten = 'drohne_einschalten' in request.form
        app_startet = 'app_startet' in request.form
        kompass_kalibrieren = 'kompass_kalibrieren' in request.form
        keine_warnungen = 'keine_warnungen' in request.form
        gps_empfang = 'gps_empfang' in request.form
        verbindung_voller_ausschlag = 'verbindung_voller_ausschlag' in request.form
        akkuladezustand = 'akkuladezustand' in request.form
        flugmodus_p = 'flugmodus_p' in request.form
        startplatz_fest = 'startplatz_fest' in request.form
        automatischen_start_einleiten = 'automatischen_start_einleiten' in request.form
        aufsteigen = 'aufsteigen' in request.form
        keine_warnmeldungen = 'keine_warnmeldungen' in request.form
        homepoint_gesetzt = 'homepoint_gesetzt' in request.form
        schwebeflug = 'schwebeflug' in request.form
        drehen_360 = 'drehen_360' in request.form
        gieren = 'gieren' in request.form
        sinkflug = 'sinkflug' in request.form
        akkustand_flugziel = 'akkustand_flugziel' in request.form
        anflug_landezone_frei = 'anflug_landezone_frei' in request.form
        landezone_frei = 'landezone_frei' in request.form
        landezone_anfliegen = 'landezone_anfliegen' in request.form
        kamera_herunterschwenken = 'kamera_herunterschwenken' in request.form
        drohne_abwenden = 'drohne_abwenden' in request.form
        sinken_landegeschwindigkeit = 'sinken_landegeschwindigkeit' in request.form
        motoren_abschalten = 'motoren_abschalten' in request.form
        ort = request.form['ort']
        datum = datetime.strptime(request.form['datum'], '%Y-%m-%d')
        unterschrift = request.form['unterschrift']
        
        checkliste = DrohnenCheckliste(
            startplatz_eingerichtet=startplatz_eingerichtet,
            fernsteuerung_einschalten=fernsteuerung_einschalten,
            bildschirm_schaltet_ein=bildschirm_schaltet_ein,
            rotoren_ueberpruefen=rotoren_ueberpruefen,
            drohne_einschalten=drohne_einschalten,
            app_startet=app_startet,
            kompass_kalibrieren=kompass_kalibrieren,
            keine_warnungen=keine_warnungen,
            gps_empfang=gps_empfang,
            verbindung_voller_ausschlag=verbindung_voller_ausschlag,
            akkuladezustand=akkuladezustand,
            flugmodus_p=flugmodus_p,
            startplatz_fest=startplatz_fest,
            automatischen_start_einleiten=automatischen_start_einleiten,
            aufsteigen=aufsteigen,
            keine_warnmeldungen=keine_warnmeldungen,
            homepoint_gesetzt=homepoint_gesetzt,
            schwebeflug=schwebeflug,
            drehen_360=drehen_360,
            gieren=gieren,
            sinkflug=sinkflug,
            akkustand_flugziel=akkustand_flugziel,
            anflug_landezone_frei=anflug_landezone_frei,
            landezone_frei=landezone_frei,
            landezone_anfliegen=landezone_anfliegen,
            kamera_herunterschwenken=kamera_herunterschwenken,
            drohne_abwenden=drohne_abwenden,
            sinken_landegeschwindigkeit=sinken_landegeschwindigkeit,
            motoren_abschalten=motoren_abschalten,
            ort=ort,
            datum=datum,
            unterschrift=unterschrift
        )
        
        db.session.add(checkliste)
        db.session.commit()
        
        return render_template('drohnen_checkliste.html', success=True, footer_text=FOOTER_TEXT, is_authenticated=is_authenticated)

    return render_template('drohnen_checkliste.html', footer_text=FOOTER_TEXT, is_authenticated=is_authenticated)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['STATIC_FOLDER'], filename)

if __name__ == '__main__':
    app.run(ssl_context=None, debug=True)

# Admin-Ansicht
admin = Admin(app, name='Admin', template_mode='bootstrap3')
admin.add_view(ModelView(DrohnenCheckliste, db.session))
admin.add_view(ModelView(Hydrant, db.session))
admin.add_view(ModelView(HydrantData, db.session))

@app.route('/admin_hydranten', methods=['GET', 'POST'])
def admin_hydranten():
    if request.method == 'POST':
        nummer = request.form['nummer']
        standortbeschreibung = request.form['standortbeschreibung']
        utm_koordinate = request.form['utm_koordinate']
        gps_daten = request.form['gps_daten']

        # Create new Hydrant object (assuming there's a Hydrant class in your models)
        new_hydrant = Hydrant(
            nummer=nummer,
            standortbeschreibung=standortbeschreibung,
            utm_koordinate=utm_koordinate,
            gps_daten=gps_daten
        )
        db.session.add(new_hydrant)
        db.session.commit()

        return redirect('/admin_hydranten')  # Refresh the page after saving

    # Fetch all hydrants to display in the admin interface
    hydrants = Hydrant.query.all()
    return render_template('admin_hydranten.html', hydrants=hydrants)

from datetime import datetime

@app.route('/hydrantenpflege', methods=['GET', 'POST'])
def hydranten_data_entry():
    hydrants = Hydrant.query.all()
    hydrants_list = [{"id": h.id, "nummer": h.nummer, "standortbeschreibung": h.standortbeschreibung} for h in hydrants]
    selected_hydrant_id = request.args.get('hydrant_id', None)
    selected_hydrant_data = []

    if request.method == 'POST':
        hydrant_id = request.form.get('hydrant')
        datum = datetime.strptime(request.form.get('datum'), '%Y-%m-%d')
        bemerkung = request.form.get('bemerkung')
        wert_1 = request.form.get('wert_1', None)
        wert_2 = request.form.get('wert_2', None)
        wert_3 = request.form.get('wert_3', None)
        wert_4 = request.form.get('wert_4', None)

        new_data = HydrantData(
            hydrant_id=hydrant_id,
            datum=datum,
            bemerkung=bemerkung,
            wert_1=wert_1,
            wert_2=wert_2,
            wert_3=wert_3,
            wert_4=wert_4
        )

        db.session.add(new_data)
        db.session.commit()

        return redirect(url_for('hydranten_data_entry', hydrant_id=hydrant_id))

    if selected_hydrant_id:
        selected_hydrant_data = HydrantData.query.filter_by(hydrant_id=selected_hydrant_id).all()

    return render_template(
        'hydrantenpflege.html',
        hydrants=hydrants_list,
        selected_hydrant_id=selected_hydrant_id,
        selected_hydrant_data=selected_hydrant_data
    )


if __name__ == '__main__':
    app.run(debug=True)
