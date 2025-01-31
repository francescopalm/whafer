# WhaFeR - WhatsApp Forensic Reporter

WhaFeR, è software sviluppato a scopo didattico per l'analisi forense dei backup WhatsApp.

## Requisiti

•	Python 3.13 (o superiore): \
https://www.python.org/downloads/ \
(Assicurarsi che durante l’installazione in ambiente Windows sia spuntata l’opzione “Add Python 3.x to PATH”)

•	Visual Studio C++ Build Tools (per Windows): \
https://aka.ms/vs/17/release/vs_BuildTools.exe

•	Android Debug Bridge (ADB): \
https://developer.android.com/tools/releases/platform-tools?hl=it \
(Assicurarsi di aggiungere adb.exe alla variabile d’ambiente PATH)

## Installazione

Per installare WhaFeR è necessario lanciare da riga di comando (cmd o Windows PowerShell su PC Windows) il seguente comando:

```
pip install git+https://github.com/francescopalm/whafer.git
```

## Uso

Per avviare WhaFeR è ora dunque sufficiente lanciare il comando:

```
whafer-gui
```

## Changelog

### [0.2.1] – 30-01-2025
Sviluppo a cura di: Francesco Palmisano

### Modifiche e implementazioni
•	Implementata visualizzazione delle conversazioni con i dettagli relativi ad ogni singolo messaggio scambiato \
•	Aggiunta verifica delle dipendenze all’avvio dell’applicativo \
•	Aggiunta possibilità di esportare i report anche in formato PDF \
•	Implementata associazione numero telefonico -> nome del contatto salvato in rubrica \

### [0.2.0] – 07-11-2024
Sviluppo a cura di: Francesco Palmisano

### Bugfix
•	Ripristino query SQL eseguite su “msgstore.db” \
•	Ripristino decrittazione di file cifrati mediante wa-crypt-tools \
•	Corretta esportazione in .csv dei report desiderati, utilizzando “;” come separatore dei valori \
•	Corrette impostazioni della UI settate in modo erroneo all’avvio \
•	Corretta elencazione di “Me stesso” nell’elenco dei partecipanti dei gruppi \
•	Corretta possibilità di annullare l’apertura di un progetto precedente o importazione degli artefatti da percorso locale senza errori \

### Modifiche e implementazioni
•	Aggiunta possibilità di automatizzare l’estrazione degli artefatti da uno smartphone Android \
•	Implementata analisi (facoltativa) dei file “com.whatsapp_preferences_light.xml” e “startup_prefs.xml” \
•	Aggiunta funzionalità “Riepilogo” con un overview delle informazioni di base ricavate dall’analisi degli artefatti importati \
•	Implementazione funzionalità “Media” con la possibilità di estrarre i file media dal dispositivo utilizzando un approccio forense (impedendo modifica dei metadati) \
•	Implementata analisi della tabella “sqlite_sequence” del DB “msgstore” contenente informazioni di particolare rilevanza \
•	Implementato controllo integrità progetto WhaFeR creato in precedenza \

### Migliorie
•	Utilizzata colorazione “darkgrey” per i pulsanti disabilitati \
•	Implementazione messaggi di successo relativi all’esportazione dei report richiesti \
•	Implementazione messaggi di errore relativi a problemi occorsi durante l’estrazione automatica degli artefatti da uno smartphone Android \
•	Aggiunte finestre di dialogo atte a elencare e chiarire le operazioni da compiere per il funzionamento corretto del software \
•	Migliorati i pulsanti relativi alle diverse funzionalità disponibili nell’applicazione: ora mostrano chiaramente il loro stato indicando anche in quale vista del programma ci si trova \
•	Cambio nome della funzionalità “Mostra contenuti” in “Analisi tabelle DB” e relativo restyling della vista in modo da compattare e descrivere le operazioni disponibili \
•	Aggiunta informazioni in vista di dettaglio di un singolo contatto \
•	Miglioramento generale del layout grafico, navigazione e architettura dell’informazione \

### [0.1.0] – 22-08-2023
Versione iniziale di rilascio. \
Sviluppo a cura di: Mikel12455 \
https://github.com/Mikel12455/whafer
