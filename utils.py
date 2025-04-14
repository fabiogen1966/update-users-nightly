import requests
import os
import configparser


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

