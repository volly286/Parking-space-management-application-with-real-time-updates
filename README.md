# Ghid Instalare și Configurare Aplicație

Acest ghid te va ghida pas cu pas pentru instalarea și configurarea aplicației tale folosind Python și XAMPP. Urmează instrucțiunile de mai jos pentru a instala toate componentele necesare și a pune aplicația în funcțiune.

---


## 1. Instalare Python

1. **Descarcă Python**:
   - Accesează [pagina oficială Python](https://www.python.org/downloads/).
   - Apasă pe butonul "Download Python" pentru a descărca versiunea 3.9.10.
   - Selectează **Windows Installer (64-bit)**, ca în imaginea de mai sus.

2. **Instalează Python**:
   - După descărcare, deschide fișierul și apasă dublu click pe el.
   - Asigură-te că ai bifat opțiunea **Add Python to PATH**.
   - Apasă pe **Install Now** și confirmă în promptul de siguranță cu **Yes**.
   - La finalizarea instalării, apasă pe **Close**.


---

## 2. Instalare XAMPP

1. **Descarcă XAMPP**:
   - Accesează [pagina oficială XAMPP](https://www.apachefriends.org/ro/download.html).
   - Apasă pe butonul **Download** și descarcă cea mai recentă versiune (8.2.12).

2. **Instalează XAMPP**:
   - După descărcare, deschide fișierul și urmează pașii din instalare:
     - Apasă pe **Next** pentru fiecare fereastră de instalare, ca în imaginea de mai sus.
     - La final, apasă pe **Finish**.


---

## 3. Crearea și Activarea Virtual Environment pentru Python

1. **Creare Virtual Environment**:
   - Deschide un terminal (CMD) și navighează în folderul unde vrei să creezi proiectul.
   - Folosește comanda:
     ```bash
     python -m venv env
     ```

2. **Activare Virtual Environment**:
   - Navighează la:
     ```bash
     cd env/Scripts
     ```
   - Activează mediul virtual cu comanda:
     ```bash
     activate.bat
     ```

---

## 4. Instalarea Librăriilor Necesare

În virtual environment-ul activat, instalează librăriile necesare folosind `pip`:

```bash
pip install flask
pip install flask_mysqldb
pip install flask_bcrypt
pip install flask_ngrok2
pip install flask_socketio
```

## 5. Configurarea Bazei de Date

### Pornirea XAMPP:
- Deschide **XAMPP Control Panel** și pornește serviciile **Apache** și **MySQL**.

### Configurarea Bazei de Date:
1. Apasă pe **Admin** lângă **MySQL** pentru a accesa **phpMyAdmin**.
2. Creează o bază de date numită **Proiect** și importă fișierul `proiect.sql` (îl poți descărca din proiectul tău).
3. Verifică dacă sunt create tabelele **users** și **parking_spots**.

---

## 6. Configurarea Aplicației

- Asigură-te că fișierele `app.py`, folderul `static` și `templates` sunt prezente.

### Pornirea Aplicației:
- În terminal, navighează la folderul aplicației și folosește comanda:
  ```bash
  python app.py

