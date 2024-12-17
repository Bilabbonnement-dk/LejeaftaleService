# LejeaftaleService
Lejeaftale service står får registrering og opdatering af lejeaftaler. Den fungerer som en hoved mikroservicen i biludlejningssystemet og interagerer med andre tjenester som SkadesService for skadesrapportering, og RapportService for forretnings udviklings formål.

Denne Readme fil beskriver alle tilgængelige endepunkter, deres formål, nødvendige input og de forventede svar.

## Funktioner
- Oprette nye lejeaftaler.
- Indhente aktive og inaktive aftaler.
- Beregn lejeomkostninger for specifikke kunder.
- Kommunikere med andre mikrotjenester for at hente relaterede data.

---

## Arkitektur
Microservicen kommunikere med:
1. **SkadesService**: For skade rapportering.
2. **RapportService**: For data rapportering.
3. **Database**: SQLite database for persistent storage of agreements.
4. **API Gateway** (skal vi lave den????): For dirigere clientens forspørglser.

---

System Arkitektur:
                                 [RapportService]
                                    |
Client --> [API Gateway] --> [LejeaftaleService] --> [SQLite Database]
                                    |
                                 [SkadesService]

---

## Forudsætninger
- Python 3.8 eller højere
- Flask 2.x
- SQLite til databasen
- Swagger UI eller Postman til API-testning

---

## Opsætning og installation

1. **Klon repository**:
   ```bash
   git clone https://github.com/yourusername/LejeaftaleService.git
   cd LejeaftaleService

2. **Opret og aktiver virtuelt minljø**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate # på macOS/Linux
   
3. **Installer dependencies**: Brug pip til at installere de nødvendige libraries.
   ```bash 
   pip install -r requirements.txt

4. **Opsæt databasen**: Kør dette script for at initialisere SQLite-databasen:
   ```bash
   python setup_database.py

5. **Kør servicen**: Start Flask serveren.
   ```bash
   python app.py

6. **Få adgang til tjenesten**: Nu køre microservicen på:
   ```bash
   http://localhost:5002

---

## Filstruktur

project/
│
├── app.py                 # Indeholder kun Flask endpoints
├── Service/               # Mappe til service logik (funktionaliteter)
│   ├── lejeaftaler.py     # Logik til lejeaftler
│   ├── connections.py     # Logik til forbindekse til andre microservice
├── requirements.txt       # Python dependencies
└── Dockerfile             # Dockerfilen indeholder instruktioner, som bruges af docker build til at bygge et docker-billede

---

## Indholdsfortegnelse

1. General information

2. Endpoints:
  1. Hent alle aftaler
  2. Hent tilgængelige biler
  3. Hent nye aftaler
  4. Opret en ny aftale
  5. Opdater aftalestatus
  6. Slet en aftale
  7. Hent kundedata
  8. Send Data til SkadesService
  9. Hent Active Lejeaftale
  10. Hent bilstatus
  11. Behandle prisdata

---

### Generel information

Basis-URL: http://localhost:5002

Indholdstype: JSON (applikation/json)

Godkendelse: Der kræves ingen godkendelse for disse endpoint som det ser ud nu. Dog kan JWT tilføjes senere, hvis det er nødvendigt.

---

## Endpoints

### 1. Fetch alle lejeaftaler
- **URL**: `/lejeaftaler`
- **Metode**: `GET`
- **Beskrive**: Hent alle lejeaftaler.

**Response**
* 200 OK
```json
[
    {
        "lejeaftale_id": 1,
        "kunde_id": 2,
        "bil_id": 3,
        "status": "Aktiv"
    }
]
```

### 2. Fetch alle ledige biler
- **URL**: `/ledigeBiler`
- **Metode**: `GET`
- **Beskrive**: Hent alle ledige biler.

**Response**
* 200 OK
```json
[
    {
        "bil_id": 3,
        "pris_pr_måned": 5000
    }
]
```

### 3. Hent ny lejeaftale
- **URL**: `/nyLejeaftaftale`
- **Metode**: `GET`
- **Beskrive**: Hent den nyeste lejeaftale.

**Response**
* 200 OK
```json
[
    {
        "lejeaftale_id": 6,
        "kunde_id": 3,
        "bil_id": 2,
        "start_dato": "2014/10/10",
        "slut_date": "2025/10/10",
        "udleveringssted": "København",
        "abonnements_varighed": 12,
        "aftale_km": 1000,
        "pris_pr_måned": 4000,
        "status": "aktiv"
    }
]
```

### 4. Opret ny lejeaftale
- **URL**: `/opretLejeaftale`
- **Metode**: `POST`
- **Beskrive**: Tilføj en ny lejeaftale.

**Request Body**:
```json
{
    "kunde_id": 1,
    "bil_id": 2,
    "start_dato": "2024-01-01",
    "slut_dato": "2024-12-31",
    "udleveringssted": "København",
    "abonnements_varighed": 12,
    "status": "aktiv"
}
```

**Response**
* 201 CREATED
```json
[
    {
      "message": "Agreement created successfully",
      "lejeaftale_id": 6,
      "ledige_biler":
        "car_costs": [
            {
              "bil_id": 1,
              "pris_pr_måned": 3000,
              "pris_i_alt": 36000
            }
        ]
    }
]
```
* 400 Bad Request: Mangler eller forkerte felter.

### 5. Opdater lejeaftale status
- **URL**: `/statusOpdatering/<int:lejeAftaleID>`
- **Metode**: `PUT`
- **Beskrive**: Opdaterer status for en eksisterende lejeaftale.

**Request Body**:
```json
{
  "agreement_id": 6,
  "status": "aktiv"
}
```

**Response**
```json
{
  "message": "Status updated successfully"
}
```
* 400 Bad Request: Mangler eller forkerte felter.

### 6. Slet lejeaftale
- **URL**: `/sletLejeAftale/<int:lejeAftaleID>`
- **Metode**: `DELETE`
- **Beskrive**: Sletter en lejeaftale via lejeaftale id.

**Response**
```json
{
  "message": "Agreement succesfully deleted"
}
```
* 400 Bad Request: Forkert input.

### 7. Henter kunde data
- **URL**: `/kundeID/<int:kundeID>`
- **Metode**: `GET`
- **Beskrive**: Henter alle aftaler for en specifik kunde.

**Response**
* 200 OK
```json
{
  "lejeaftale_id": 7,
  "kunde_id": 4,
  "bil_id": 3,
  "status": "Aktiv"
}
```
* 404 Not Found: Ingen data er fundet for den specifikke kunde
  
### 8. Send data til SkadeService
- **URL**: `/send-damage-data/new-damage`
- **Metode**: `POST`
- **Beskrive**: Sender data til skades service til håndtering.

**Request Body**
```json
{
  "bil_id": 5,
  "lejeaftale_id": 6,
  "beskrivelse": "Scratch on the door",
  "omkostninger": 1500.0
}
```

**Response**
* 200 OK
```json
{
    "message": "Damage report added successfully",
    "damage_id": 10
}

```

### 9. Hent aktive lejeaftaler
- **URL**: `/lejeaftale`
- **Metode**: `GET`
- **Beskrive**: Henter og sender aktive lejeaftaler til RapportService.

**Response**
*200 OK: Liste med aktive lejeaftaler.

### 10. Hent aktive biler 
- **URL**: `/status/<int:bil_id>`
- **Metode**: `GET`
- **Beskrive**: Henter og sender aktive biler til RapportService via bil id.

**Response**
*200 OK: Liste med aktive biler.
```json
{
    "bil_id": 5,
    "status": "Aktiv"
}
```

### 11. Henter BilID og PrisPrMåned relateret data
- **URL**: `/process-pris-data`
- **Metode**: `GET`
- **Beskrive**: Henter og sender data til RapportService via lejeaftale id.

**Response**
*200 OK
```json
{
    "message": "Price data processed successfully"
}
```

---

### Testing
Når servicen køre, kan man bruge Postman or curl til at interagere med api gateway.

For eksempel:

Status opdatering: Test LejeaftaleService ved at indsætte det ønskede lejeaftale id som parameter og den nye status ændring i json format.
PUT http://localhost:5003/statusOpdatering/3

Expected json body:

{
  "lejeaftale_id": 2,
  "status": "Aktiv"
}

Expected response:

{
  "message": "Status updated successfully"
}























