from utils import *

# Esempio di utilizzo
if __name__ == "__main__":
    # Puoi chiamare la funzione senza argomenti per usare l'URL predefinito
    display_message("INFO", "Inizio elaborazione...")
    display_message("INFO", "Inizio download file CSV da URL predefinito...")
    download_file()
    display_message("INFO", "Download file CSV completato...")
    display_message("INFO", "Inizio caricamento file CSV in PostgreSQL...")   
    # Oppure puoi specificare un URL diverso
    # download_file("https://esempio.com/altro_file.csv")
    load_csv_to_postgresql()
    display_message("INFO", "Caricamento file CSV in PostgreSQL completato.")
    display_message("INFO", "Fine elaborazione.")