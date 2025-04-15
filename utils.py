import requests
import os
import configparser
import csv
import psycopg2

from datetime import datetime
from colorama import init, Fore, Style

# Inizializza colorama (necessario su Windows)
init(autoreset=True)


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

        display_message("INFO",f"File scaricato con successo da....: {url}")
        display_message("INFO",f"Nome file scaricato...............: {filename}")
        display_message("INFO",f"Salvataggio effettuato in.........: {file_path}")
    except requests.RequestException as e:
        display_message("ERROR",f"Errore durante il download del file: {e}")
    except IOError as e:
        display_message("ERROR",f"Errore durante il salvataggio del file: {e}")
    except Exception as e:
        display_message("ERROR",f"Errore imprevisto: {e}")
        
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
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            headers = next(csvreader)  # Leggi l'intestazione

            # Prepara la query di inserimento
            insert_query = f"INSERT INTO {table_name} ({','.join(headers)}) VALUES ({','.join(['%s']*len(headers))})"

            # Inserisci i dati riga per riga
            for row in csvreader:
                cur.execute(insert_query, row)

        # Commit delle modifiche
        conn.commit()
        display_message("INFO",f"Caricamento dati completato nella tabella: {table_name}")
        
    except (Exception, psycopg2.Error) as error:
        # Gestione degli errori
        display_message("ERROR",f"Errore durante il caricamento del file CSV: {error}")
        display_message("ERROR",f"Ultima riga elaborata: {row}")

    finally:
        # Chiudi la connessione al database
        if conn:
            cur.close()
            conn.close()
            display_message("INFO","Connessione al database chiusa.")

def write_log(message):
    # Scrivi un messaggio di log su un file
    with open('log.txt', 'a') as log_file:
        log_file.write(f"{message}\n")

def display_message(level: str, message: str) -> None:
    """
    Mostra un messaggio formattato con timestamp, livello e colore.

    Args:
        level (str): Il livello del messaggio (es. 'INFO', 'WARN', 'ERROR').
        message (str): Il contenuto del messaggio.
    """
    timestamp = datetime.now().strftime("%Y-%d-%m %H:%M:%S")
    level = level.upper()

    # Associa il colore in base al livello
    if level == "INFO":
        color = Fore.GREEN
    elif level == "WARN":
        color = Fore.YELLOW
    elif level == "ERROR":
        color = Fore.RED
    else:
        color = Fore.WHITE  # Default per livelli sconosciuti

    formatted_message = f"{color}[{timestamp}] - {level} - {message}{Style.RESET_ALL}"
    print(formatted_message)