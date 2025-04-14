import requests
import os
import configparser
import csv
import psycopg2

def download_file(url=None):
    # Leggi il file di configurazione
    config = configparser.ConfigParser()
    # Assicurati che il file config.ini esista nella stessa directory dello script
    config.read('config.ini')

    # Ottieni la directory di staging e l'URL dal file di configurazione
    staging_dir = config.get('Directories', 'dir-staging')
    default_url = config.get('URLs', 'download_url')

    # Usa l'URL fornito come parametro, se presente, altrimenti usa quello del file di configurazione
    url = url or default_url

    # Assicurati che la directory di staging esista
    os.makedirs(staging_dir, exist_ok=True)

    # Estrai il nome del file dall'URL
    filename = os.path.basename(url)
    file_path = os.path.join(staging_dir, filename)

    try:
        # Scarica il file
        response = requests.get(url)
        response.raise_for_status()  # Solleva un'eccezione per risposte HTTP non riuscite

        # Salva il file nella directory di staging
        with open(file_path, 'wb') as file:
            file.write(response.content)

        print(f"***********************************************\n")
        print(f"- File scaricato con successo da....: {url}\n")
        print(f"- Salvataggio effettuato in.........: {file_path}\n")
        print(f"***********************************************\n")

    except requests.RequestException as e:
        print(f"Errore durante il download del file: {e}")
    except IOError as e:
        print(f"Errore durante il salvataggio del file: {e}")

def load_csv_to_postgresql():
    config = configparser.ConfigParser()
    # Assicurati che il file config.ini esista nella stessa directory dello script
    config.read('config.ini')

    # Ottieni la directory di staging e l'URL dal file di configurazione
    csv_directory = config.get('Directories', 'dir-staging')
    csv_filename = config.get('Directories', 'staging-file')
    table_name = config.get('DB', 'stage-table')

     # Parametri di connessione al database
    db_params = {
        'host': config.get('DB','host'),
        'database': config.get('DB','database'),
        'user': config.get('DB', 'user'),
        'password': config.get('DB', 'password')
    }

    # Percorso completo del file CSV
    csv_path = os.path.join(csv_directory, csv_filename)

    try:
        # Connessione al database
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        # Esegui TRUNCATE sulla tabella
        cur.execute(f"TRUNCATE TABLE {table_name}")

        # Apri e leggi il file CSV
        with open(csv_path, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            headers = next(csvreader)  # Leggi l'intestazione

            # Prepara la query di inserimento
            insert_query = f"INSERT INTO {table_name} ({','.join(headers)}) VALUES ({','.join(['%s']*len(headers))})"

            # Inserisci i dati riga per riga
            for row in csvreader:
                cur.execute(insert_query, row)

        # Commit delle modifiche
        conn.commit()
        print(f"Dati caricati con successo nella tabella {table_name}")

    except (Exception, psycopg2.Error) as error:
        print(f"Errore durante l'esecuzione dello script: {error}")

    finally:
        # Chiudi la connessione al database
        if conn:
            cur.close()
            conn.close()
            print("Connessione al database chiusa.")
