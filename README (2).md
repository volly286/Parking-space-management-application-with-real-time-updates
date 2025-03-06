
# Aplicatie de Management a Locurilor de Parcare

## 1. Descriere

Aplicatia de management a locurilor de parcare permite utilizatorilor să rezerve un loc de parcare și vizualizeze disponibilitatea acestora în timp real.

## 2. Resurse Aplicație

- Python: [Link de descărcare Python](https://www.python.org/downloads/)
  - Apasă butonul de **Download** ca în imaginea de mai sus.
  - Descarcă versiunea 3.9.10 apasând pe butonul de download din dreptul acesteia.
  - Scroll mai jos până ajungi în dreptul acestei imagini de unde vei selecta **Windows Installer (64-bit)**.
  - După ce ai descărcat fișierul, deschide-l apasând dublu click pe acesta.
  - Asigură-te că ai setările corect configurate, apoi apasă pe **INSTALL NOW**.
  - În promptul de siguranță, apasă pe **Yes**.
  - După finalizarea instalării, apasă pe **Close**.

- XAMPP: [Link de descărcare XAMPP](https://www.apachefriends.org/ro/download.html)
  - Apasă pe butonul de **Descărcare**, vom descărca cea mai actualizată versiune 8.2.12.
  - După ce ai descărcat fișierul, deschide-l apasând dublu click pe acesta.
  - În promptul de siguranță, apasă pe **Yes**.
  - Apasă pe **Next**.
  - Apasă pe **Finish** pentru a finaliza instalarea.

## 3. Configurarea Bazei de Date

### Pornirea XAMPP:
1. Deschide XAMPP Control Panel și pornește serviciile Apache și MySQL.
  
### Configurarea Bazei de Date:
1. Apasă pe **Admin** lângă MySQL pentru a accesa phpMyAdmin.
2. Creează o bază de date numită **Proiect** și importă fișierul **proiect.sql** (îl poți descărca din proiectul tău).
3. Verifică dacă sunt create tabelele `users` și `parking_spots`.

## 4. Configurarea Aplicației

### Verifică dacă Python este instalat corect:
În CMD, folosește comanda:
```bash
python --version
```

### Navighează în folderul principal al aplicației:
- Asigură-te că fișierele `app.py`, folderul `static` și `templates` sunt prezente.

### Pornirea Aplicației:
- În terminal, navighează la folderul aplicației și folosește comanda:
  ```bash
  python app.py
  ```
- Vei primi linkuri de acces în **CMD** pentru a deschide aplicația în browser.

### Modifică fișierul `script.js`:
1. Deschide fișierul `script.js` din folderul `static/js/`.
2. Caută secvența de cod:
   ```html
   <script>
       var socket = io.connect('aici veti pune linkul copiat');
   </script>
   ```
3. Înlocuiește `aici veti pune linkul copiat` cu linkul generat de **ngrok**.

## 5. Posibile Erori și Rezolvarea Lor

### Eroare NGROK - ERR_NGROK108:
În momentul introducerii comenzii `python app.py`, **ngrok** poate afișa o eroare de tipul **ERR_NGROK108** fără a afișa linkurile de conectare. Pentru a rezolva această eroare, apasă **CTRL + C** o singură dată pentru a opri procesul, iar apoi reîncearcă să rulezi comanda.

### Eroare la Înlocuirea Linkului în `script.js`:
Atunci când înlocuiești în fișierul `script.js` linkul generat de ngrok, asigură-te că linkul respectă forma corectă:
```bash
https://linkultau/
```
Dacă nu iei în considerare **HTTPS** și **/**, actualizările în timp real nu vor funcționa corect.

## 6. Funcții Cheie ale Aplicației

### Funcția de Rezervare (Python + Flask)
```python
@app.route('/reserve/<int:spot_id>')
def reserve(spot_id):
    user_id = session.get('UserID')
    if not user_id:
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    # Verifica daca utilizatorul are deja un loc rezervat
    cur.execute("SELECT * FROM parking_spots WHERE reserved_by = %s", (user_id,))
    if cur.fetchone():
        flash('Aveți deja un loc rezervat', 'error')
        cur.close()
        return redirect(url_for('index'))
    # Verifica daca spatiul este disponibil
    cur.execute("SELECT * FROM parking_spots WHERE spot_id = %s AND is_reserved = False", (spot_id,))
    spot = cur.fetchone()
    if spot:
        # Preia numarul de inmatriculare din baza de date
        cur.execute("SELECT license_number FROM users WHERE id = %s", (user_id,))
        user_data = cur.fetchone()
        user_license_number = user_data['license_number']
        # Rezerva locul
        cur.execute("UPDATE parking_spots SET is_reserved = True, reserved_by = %s, license_number = %s WHERE spot_id = %s", 
                    (user_id, user_license_number, spot_id))
        mysql.connection.commit()
        # Emite eveniment pentru actualizare in timp real
        socketio.emit('update_parking_spot', {'spot_id': spot_id, 'status': 'reserved', 'license_number': user_license_number})
        cur.close()
    return redirect(url_for('index'))
```

### Funcția de Rezervare (Javascript)
```javascript
function reserveSpot(spotId) {
    window.location.href = '/reserve/' + spotId;
}

var socket = io.connect('https://4eb3-213-233-104-136.ngrok-free.app/'); // link creat de ngrok
socket.on('update_parking_spot', function(data) {
    var spotElement = document.getElementById("spot-" + data.spot_id);
    if (spotElement) {
        var statusText = 'Locul ' + data.spot_id;
        if (data.status === 'reserved') {
            spotElement.classList.add('reserved');
            spotElement.removeAttribute('onclick');
            statusText += ' (Rezervat de ' + data.license_number + ')';
        } else {
            spotElement.classList.remove('reserved');
            spotElement.setAttribute('onclick', 'reserveSpot("' + data.spot_id + '")');
            statusText += ' (Disponibil)';
        }
        spotElement.textContent = statusText;
    }
});
```

## 7. Linkuri Utile
- [YouTube Tutorial](https://www.youtube.com/watch?v=m7ucpSTtqEo&ab_channel=CodegnanDestination)
- [ChatGPT - Conversație 1](https://chat.openai.com/share/4494b6fb-97c3-4025-a110-8e7da4b30617)
- [ChatGPT - Conversație 2](https://chat.openai.com/share/60846d0d-7ba3-479b-af92-b30364f4ac84)
