from flask import Flask, render_template, url_for, request, redirect, flash, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

con = mysql.connector.connect(
	host='localhost',
	port='3306',
	user='root',
	passwd='',
	
	database='evidencija_studenata'
)

mycursor = con.cursor(dictionary=True)

app = Flask(__name__)

app.secret_key='tajni_kljuc'

#-----------------------------------------------> Login <-------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def Login():
	if request.method=='GET':
		return render_template('login.html')
	elif request.method=='POST':
		forma=request.form
		upit="SELECT * FROM korisnici WHERE kemail=%s"
		vrednost=(forma['kemail'],)
		mycursor.execute(upit, vrednost)
		korisnik=mycursor.fetchone()

		if(korisnik is not None):
			# if(korisnik['lozinka']==forma['lozinka']):
			# 	session['ulogovani_korisnik']=str(korisnik)
			# 	return redirect(url_for('Studenti'))
			if check_password_hash(korisnik['lozinka'], forma['lozinka']):
				session['ulogovani_korisnik']=str(korisnik)
				return redirect(url_for('Studenti'))
			else:
				flash("Pogrešna lozinka!")
				return redirect(request.referrer)
		else:
			flash("Korisnik sa navedenim korisičkim imenom ne postoji.")
			return redirect(request.referrer)

def Logged():
 if 'ulogovani_korisnik' in session:
 	return True
 else:
 	return False


@app.route('/logout')
def Logout():
	session.pop('ulogovani_korisnik', None)
	return redirect(url_for('Login'))

@app.route('/')
def Home():
	return render_template("login.html")


#-----------------------------------------------> Studenti <-----------------------------------------------------

@app.route('/studenti')
def Studenti():

	if Logged():
		upit = "SELECT * FROM studenti"
		mycursor.execute(upit)
		studenti = mycursor.fetchall()
		return render_template("studenti.html", studenti=studenti)
	else:
		return redirect(url_for("Login"))	



@app.route('/student/<id>')
def Student(id):

	if Logged():
		upit = "SELECT * FROM studenti WHERE id = %s"
		vrednost = (id,)
		mycursor.execute(upit, vrednost)
		student = mycursor.fetchone()
		upit = "SELECT * FROM predmeti"
		mycursor.execute(upit)
		predmeti = mycursor.fetchall()
		upit = """
			SELECT *
			FROM predmeti
			JOIN ocene
			ON predmeti.id = ocene.predmet_id
			WHERE ocene.student_id = %s
		"""
		vrednost = (id,)
		mycursor.execute(upit, vrednost)
		ocene = mycursor.fetchall()
		return render_template("student.html", student=student, predmeti = predmeti, ocene = ocene)
	else:
		return redirect(url_for('Login'))


@app.route('/novistudent', methods=['GET', 'POST'])
def NoviStudent():

	if Logged():

		if request.method == 'POST':
			broj_indeksa = request.form['broj_indeksa']
			ime = request.form['ime']
			ime_roditelja = request.form['ime_roditelja']
			prezime = request.form['prezime']
			email = request.form['email']
			broj_telefona = request.form['broj_telefona']
			godina_studija = request.form['godina_studija']
			datum_rodjenja = request.form['datum_rodjenja']
			jmbg = request.form['jmbg']
			

			mycursor.execute("INSERT INTO studenti (broj_indeksa, ime, ime_roditelja, prezime, email, broj_telefona, godina_studija, datum_rodjenja, jmbg) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (broj_indeksa, ime, ime_roditelja, prezime, email, broj_telefona, godina_studija, datum_rodjenja, jmbg))
			con.commit()

			return redirect(url_for('Studenti'))

		else:
			return render_template('student_novi.html')
	else:
		return redirect(url_for('Login'))	


@app.route('/student_izmena', methods=['GET', 'POST'])
def StudentIzmena():

	if Logged():

		if request.method == 'POST':
			id_data = request.form['id']
			broj_indeksa = request.form['broj_indeksa']
			ime = request.form['ime']
			ime_roditelja = request.form['ime_roditelja']
			prezime = request.form['prezime']
			email = request.form['email']
			broj_telefona = request.form['broj_telefona']
			godina_studija = request.form['godina_studija']
			datum_rodjenja = request.form['datum_rodjenja']
			jmbg = request.form['jmbg']

			mycursor.execute("UPDATE studenti SET broj_indeksa=%s, ime=%s, ime_roditelja=%s, prezime=%s, email=%s, broj_telefona=%s, godina_studija=%s, datum_rodjenja=%s, jmbg=%s WHERE id=%s", (broj_indeksa, ime, ime_roditelja, prezime, email, broj_telefona, godina_studija, datum_rodjenja, jmbg, id_data))
			flash("Izmena je uspešno izvršena.")
			con.commit()

			return redirect(request.referrer)
	else:
		return redirect(url_for('Login'))


@app.route('/student_brisanje/<string:id_data>', methods = ['GET', 'POST'])
def StudentBrisanje(id_data):

	if Logged():

		mycursor = con.cursor()
		upit= "DELETE FROM studenti WHERE id = %s"
		vrednost = (id_data,)
		mycursor.execute(upit, vrednost)
		flash("Student je obrisan.")
		con.commit()

		return redirect(url_for('Studenti'))
	else:
		return redirect(url_for('Login'))

#-----------------------------------------------> Korisnici <-----------------------------------------------------

@app.route('/korisnici')
def Korisnici():

	if Logged():
		upit = "SELECT * FROM korisnici"
		mycursor.execute(upit)
		korisnici = mycursor.fetchall()
		return render_template('korisnici.html', korisnici=korisnici)
	else:
		return redirect(url_for('Login'))


@app.route('/novikorisnik', methods=['GET', 'POST'])
def NoviKorisnik():

	if Logged():
		
		if request.method == 'GET':
			return render_template('korisnik_novi.html')
		elif request.method == 'POST':
			forma = request.form
			upit = "INSERT INTO korisnici (kime, kprezime, kemail, lozinka) VALUES (%s, %s, %s, %s)"
			hash_lozinka = generate_password_hash(forma['lozinka'])
			vrednosti = (forma['kime'], forma['kprezime'], forma['kemail'], hash_lozinka)
			mycursor.execute(upit, vrednosti)
			con.commit()
			return redirect(url_for('Korisnici'))
	else:
		return redirect(url_for('Login'))


@app.route('/korisnik_izmena', methods=['GET', 'POST'])
def KorisnikIzmena():

	if Logged():
		if request.method == 'POST':
			id_data = request.form['id']
			kime = request.form['kime']
			kprezime = request.form['kprezime']
			kemail = request.form['kemail']
			lozinka = generate_password_hash(request.form['lozinka'])

			mycursor.execute("UPDATE korisnici SET kime=%s, kprezime=%s, kemail=%s, lozinka=%s WHERE id=%s", (kime, kprezime, kemail, lozinka, id_data))
			flash("Izmena je uspešno izvršena.")
			con.commit()

			return redirect(url_for('Korisnici'))
	else:
		redirect(url_for('Login'))

@app.route('/korisnik_brisanje/<string:id_data>', methods = ['GET', 'POST'])
def KorisnikBrisanje(id_data):

	if Logged():
		mycursor = con.cursor()
		upit= "DELETE FROM korisnici WHERE id = %s"
		vrednost = (id_data,)
		mycursor.execute(upit, vrednost)
		flash("Korisnik je obrisan.")
		con.commit()

		return redirect(url_for('Korisnici'))
	else:
		return redirect(url_for('Login'))

#-----------------------------------------------> Predmeti <-----------------------------------------------------

@app.route('/predmeti')
def Predmeti():

	if Logged():
		mycursor = con.cursor(dictionary=True)
		mycursor.execute("SELECT * FROM predmeti")
		data = mycursor.fetchall()
		mycursor.close()
		return render_template('predmeti.html', predmeti=data)
	else:
		return redirect(url_for('Login'))


@app.route('/predmet_izmena', methods=['GET', 'POST'])
def PredmetIzmena():

	if Logged():
		if request.method == 'POST':
			id_data = request.form['id']
			sifra = request.form['sifra']
			naziv = request.form['naziv']
			godina_studija = request.form['godina_studija']
			espb = request.form['espb']
			izbor = request.form['izbor']

			mycursor.execute("UPDATE predmeti SET sifra=%s, naziv=%s, godina_studija=%s, espb=%s, izbor=%s  WHERE id=%s", (sifra, naziv, godina_studija, espb, izbor, id_data))
			flash("Izmena je uspešno izvršena.")
			con.commit()

			return redirect(url_for('Predmeti'))
	else:
		return redirect(url_for('Login'))


@app.route('/predmet_brisanje/<string:id_data>', methods = ['GET', 'POST'])
def PredmetBrisanje(id_data):
	if Logged():
		mycursor = con.cursor()
		upit= "DELETE FROM predmeti WHERE id = %s"
		vrednost = (id_data,)
		mycursor.execute(upit, vrednost)
		flash("Predmet je obrisan.")
		con.commit()

		return redirect(url_for('Predmeti'))
	else:
		return redirect(url_for('Login'))


@app.route('/novipredmet', methods=['GET', 'POST'])
def NoviPredmet():

	if Logged():

		if request.method == 'POST':
			sifra = request.form['sifra']
			naziv = request.form['naziv']
			godina_studija = request.form['godina_studija']
			espb = request.form['espb']
			izbor = request.form['izbor']


			mycursor.execute("INSERT INTO predmeti (sifra, naziv, godina_studija, espb, izbor) VALUES (%s, %s, %s, %s, %s)", (sifra, naziv, godina_studija, espb, izbor))
			con.commit()

			return redirect(url_for('Predmeti'))

		else:	
			return render_template('predmet_novi.html')
	else:
		return redirect('Login')


@app.route("/ocena_nova/<id>", methods=["POST"])
def Nova_Ocena(id):
    if Logged():
        # ----------> Dodavanje ocene <----------
        upit = """
            INSERT INTO ocene(student_id, predmet_id, ocena, datum)
            VALUES(%s, %s, %s, %s)
        """
        forma = request.form
        vrednosti = (id, forma['predmet_id'], forma['ocena'], forma['datum'])
        mycursor.execute(upit, vrednosti)
        flash("Ocena je uspešno dodata.")
        con.commit()
        # ----------> Prosek ocena <----------
        upit = "SELECT AVG(ocena) AS rezultat FROM ocene WHERE student_id=%s"
        vrednost = (id,)
        mycursor.execute(upit, vrednost)
        prosek_ocena = mycursor.fetchone()
        # ----------> Ukupno ESPB <----------
        upit = "SELECT SUM(espb) AS rezultat FROM predmeti WHERE id IN (SELECT predmet_id FROM ocene WHERE student_id=%s)"
        vrednost = (id,)
        mycursor.execute(upit, vrednost)
        espb = mycursor.fetchone()
        # ----------> Update student <----------
        upit = "UPDATE studenti SET espb=%s, prosek_ocena=%s WHERE id=%s"
        vrednosti = (espb['rezultat'], prosek_ocena['rezultat'], id)
        mycursor.execute(upit, vrednosti)
        con.commit()
        return redirect(url_for('Student', id=id))
    else:
        return redirect(url_for('Login'))

@app.route('/ocena_brisanje/<student_id>/<ocena_id>')
def Ocena_Brisanje(student_id, ocena_id):
    if Logged():
        upit = "DELETE FROM ocene WHERE id=%s"
        vrednost=(ocena_id,)
        mycursor.execute(upit, vrednost)
        flash("Ocena je obrisana.")
        con.commit()
        # # ----------> Prosek ocena <----------
        upit = "SELECT AVG(ocena) AS rezultat FROM ocene WHERE student_id=%s"
        vrednost = (student_id,)
        mycursor.execute(upit, vrednost)
        prosek_ocena = mycursor.fetchone()
        # ----------> Ukupno ESPB <----------
        upit = "SELECT SUM(espb) AS rezultat FROM predmeti WHERE id IN (SELECT predmet_id FROM ocene WHERE student_id=%s)"
        vrednost = (student_id,)
        mycursor.execute(upit, vrednost)
        espb = mycursor.fetchone()
        # ----------> Update student <----------
        upit = "UPDATE studenti SET espb=%s, prosek_ocena=%s WHERE id=%s"
        vrednosti = (espb['rezultat'], prosek_ocena['rezultat'], student_id)
        mycursor.execute(upit, vrednosti)
        con.commit()
        return redirect(url_for('Student', id=student_id))
    else:
        return redirect(url_for('Login'))
		
app.run(debug=True)

