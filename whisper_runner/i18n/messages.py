"""All interface text and its translations. Add a language by adding a column here and a
line in UI_LANGS (i18n/__init__.py)."""


# Each English text and its translations, in this order. Text missing here is shown in English.
# Polish and Ukrainian put counts after a colon ("Dostępne aktualizacje: 3") so one form fits any number.
TRANSLATED = ("no", "sv", "da", "de", "es", "fr", "pl", "uk")


MESSAGES = {
    # header and file
    "Transcribe audio with OpenAI Whisper": (
        "Transkriber lyd med OpenAI Whisper", "Transkribera ljud med OpenAI Whisper",
        "Transskriber lyd med OpenAI Whisper", "Audio mit OpenAI Whisper transkribieren",
        "Transcribe audio con OpenAI Whisper", "Transcrivez de l'audio avec OpenAI Whisper",
        "Transkrybuj dźwięk za pomocą OpenAI Whisper", "Транскрибуйте аудіо за допомогою OpenAI Whisper"),
    "Checking…": (
        "Sjekker…", "Kontrollerar…", "Kontrollerer…", "Wird geprüft…",
        "Comprobando…", "Vérification…", "Sprawdzanie…", "Перевірка…"),
    "No file selected": (
        "Ingen fil valgt", "Ingen fil vald", "Ingen fil valgt", "Keine Datei ausgewählt",
        "Ningún archivo seleccionado", "Aucun fichier sélectionné", "Nie wybrano pliku", "Файл не вибрано"),
    "Choose a recording file, or drop one here.": (
        "Velg en opptaksfil, eller slipp en her.",
        "Välj en inspelning, eller släpp en här.",
        "Vælg en optagelse, eller slip en her.",
        "Wählen Sie eine Aufnahme oder ziehen Sie sie hierher.",
        "Elige una grabación o suéltala aquí.",
        "Choisissez un enregistrement ou déposez-le ici.",
        "Wybierz nagranie lub upuść je tutaj.",
        "Виберіть запис або перетягніть його сюди."),
    "Choose a recording file.": (
        "Velg en opptaksfil.", "Välj en inspelning.", "Vælg en optagelse.", "Wählen Sie eine Aufnahme.",
        "Elige una grabación.", "Choisissez un enregistrement.", "Wybierz nagranie.", "Виберіть запис."),
    "Choose file": (
        "Velg fil", "Välj fil", "Vælg fil", "Datei wählen",
        "Elegir archivo", "Choisir un fichier", "Wybierz plik", "Вибрати файл"),
    "Drop to open this file": (
        "Slipp for å åpne denne filen", "Släpp för att öppna filen", "Slip for at åbne filen",
        "Loslassen, um die Datei zu öffnen", "Suelta para abrir este archivo",
        "Relâchez pour ouvrir ce fichier", "Upuść, aby otworzyć ten plik", "Відпустіть, щоб відкрити цей файл"),
    "Release the mouse button to choose it.": (
        "Slipp museknappen for å velge den.",
        "Släpp musknappen för att välja den.",
        "Slip museknappen for at vælge den.",
        "Lassen Sie die Maustaste los, um sie auszuwählen.",
        "Suelta el botón del ratón para elegirlo.",
        "Relâchez le bouton de la souris pour le choisir.",
        "Zwolnij przycisk myszy, aby go wybrać.",
        "Відпустіть кнопку миші, щоб вибрати його."),
    "Choose an audio file": (
        "Velg en lydfil", "Välj en ljudfil", "Vælg en lydfil", "Audiodatei wählen",
        "Elige un archivo de audio", "Choisissez un fichier audio", "Wybierz plik audio", "Виберіть аудіофайл"),
    "Audio and video": (
        "Lyd og video", "Ljud och video", "Lyd og video", "Audio und Video",
        "Audio y vídeo", "Audio et vidéo", "Audio i wideo", "Аудіо та відео"),
    "All files": (
        "Alle filer", "Alla filer", "Alle filer", "Alle Dateien",
        "Todos los archivos", "Tous les fichiers", "Wszystkie pliki", "Усі файли"),
    "That's a folder. Choose or drop an audio file.": (
        "Det er en mappe. Velg eller slipp en lydfil.",
        "Det är en mapp. Välj eller släpp en ljudfil.",
        "Det er en mappe. Vælg eller slip en lydfil.",
        "Das ist ein Ordner. Wählen Sie eine Audiodatei oder ziehen Sie sie hierher.",
        "Eso es una carpeta. Elige o suelta un archivo de audio.",
        "C'est un dossier. Choisissez ou déposez un fichier audio.",
        "To jest folder. Wybierz lub upuść plik audio.",
        "Це папка. Виберіть або перетягніть аудіофайл."),
    "File not found": (
        "Fant ikke filen", "Filen hittades inte", "Filen blev ikke fundet", "Datei nicht gefunden",
        "Archivo no encontrado", "Fichier introuvable", "Nie znaleziono pliku", "Файл не знайдено"),
    "Can't open this file. Files on a phone connected by USB must be copied to this PC first.": (
        "Kan ikke åpne denne filen. Filer på en telefon koblet til med USB må kopieres til denne PC-en først.",
        "Kan inte öppna filen. Filer på en telefon som är ansluten via USB måste först kopieras till den här "
        "datorn.",
        "Kan ikke åbne filen. Filer på en telefon, der er tilsluttet med USB, skal først kopieres til denne pc.",
        "Diese Datei lässt sich nicht öffnen. Dateien auf einem per USB verbundenen Telefon müssen zuerst auf "
        "diesen PC kopiert werden.",
        "No se puede abrir este archivo. Los archivos de un teléfono conectado por USB deben copiarse primero "
        "a este PC.",
        "Impossible d'ouvrir ce fichier. Les fichiers d'un téléphone connecté en USB doivent d'abord être "
        "copiés sur ce PC.",
        "Nie można otworzyć tego pliku. Pliki z telefonu podłączonego przez USB trzeba najpierw skopiować na "
        "ten komputer.",
        "Не вдається відкрити цей файл. Файли з телефона, під'єднаного через USB, спершу потрібно скопіювати "
        "на цей ПК."),
    "File size: {size} · Duration: {length} · Type: {ext}": (
        "Filstørrelse: {size} · Varighet: {length} · Type: {ext}",
        "Filstorlek: {size} · Längd: {length} · Typ: {ext}",
        "Filstørrelse: {size} · Varighed: {length} · Type: {ext}",
        "Dateigröße: {size} · Dauer: {length} · Typ: {ext}",
        "Tamaño: {size} · Duración: {length} · Tipo: {ext}",
        "Taille : {size} · Durée : {length} · Type : {ext}",
        "Rozmiar pliku: {size} · Długość: {length} · Typ: {ext}",
        "Розмір файлу: {size} · Тривалість: {length} · Тип: {ext}"),
    "reading…": (
        "leser…", "läser…", "læser…", "wird gelesen…", "leyendo…", "lecture…", "odczyt…", "читання…"),
    "unknown": (  # a duration or a version
        "ukjent", "okänd", "ukendt", "unbekannt", "desconocida", "inconnue", "nieznana", "невідома"),

    # model
    "Model": ("Modell", "Modell", "Model", "Modell", "Modelo", "Modèle", "Model", "Модель"),
    "Download": (
        "Last ned", "Ladda ner", "Hent", "Herunterladen", "Descargar", "Télécharger", "Pobierz", "Завантажити"),
    "Checking your system…": (
        "Sjekker systemet ditt…", "Kontrollerar ditt system…", "Kontrollerer dit system…",
        "System wird geprüft…", "Comprobando tu sistema…", "Analyse de votre système…",
        "Sprawdzanie systemu…", "Перевірка системи…"),
    "Suggested for this PC: {model}": (
        "Anbefalt for denne PC-en: {model}", "Rekommenderas för den här datorn: {model}",
        "Anbefalet til denne pc: {model}", "Empfohlen für diesen PC: {model}",
        "Recomendado para este PC: {model}", "Recommandé pour ce PC : {model}",
        "Zalecany dla tego komputera: {model}", "Рекомендовано для цього ПК: {model}"),
    "Selected manually · suggested for this PC: {model}": (
        "Valgt manuelt · anbefalt for denne PC-en: {model}",
        "Valt manuellt · rekommenderas för den här datorn: {model}",
        "Valgt manuelt · anbefalet til denne pc: {model}",
        "Manuell gewählt · empfohlen für diesen PC: {model}",
        "Elegido manualmente · recomendado para este PC: {model}",
        "Choisi manuellement · recommandé pour ce PC : {model}",
        "Wybrany ręcznie · zalecany dla tego komputera: {model}",
        "Вибрано вручну · рекомендовано для цього ПК: {model}"),
    "Selected manually · checking your system…": (
        "Valgt manuelt · sjekker systemet ditt…", "Valt manuellt · kontrollerar ditt system…",
        "Valgt manuelt · kontrollerer dit system…", "Manuell gewählt · System wird geprüft…",
        "Elegido manualmente · comprobando tu sistema…", "Choisi manuellement · analyse de votre système…",
        "Wybrany ręcznie · sprawdzanie systemu…", "Вибрано вручну · перевірка системи…"),
    "↓ Downloading {model}…": (
        "↓ Laster ned {model}…", "↓ Laddar ner {model}…", "↓ Henter {model}…",
        "↓ {model} wird heruntergeladen…", "↓ Descargando {model}…", "↓ Téléchargement de {model}…",
        "↓ Pobieranie {model}…", "↓ Завантаження {model}…"),
    "✓ {model} is installed and ready": (
        "✓ {model} er installert og klar", "✓ {model} är installerad och redo",
        "✓ {model} er installeret og klar", "✓ {model} ist installiert und bereit",
        "✓ {model} está instalado y listo", "✓ {model} est installé et prêt",
        "✓ {model} jest zainstalowany i gotowy", "✓ {model} встановлено й готово"),
    "{model} isn't installed yet ({size}). Click Download to install it (needs internet).": (
        "{model} er ikke installert ennå ({size}). Klikk Last ned for å installere den (krever internett).",
        "{model} är inte installerad än ({size}). Klicka på Ladda ner för att installera den (kräver internet).",
        "{model} er ikke installeret endnu ({size}). Klik på Hent for at installere den (kræver internet).",
        "{model} ist noch nicht installiert ({size}). Klicken Sie auf Herunterladen, um es zu installieren "
        "(Internet erforderlich).",
        "{model} aún no está instalado ({size}). Haz clic en Descargar para instalarlo (requiere internet).",
        "{model} n'est pas encore installé ({size}). Cliquez sur Télécharger pour l'installer (connexion "
        "Internet requise).",
        "Model {model} nie jest jeszcze zainstalowany ({size}). Kliknij Pobierz, aby go zainstalować "
        "(wymaga internetu).",
        "{model} ще не встановлено ({size}). Натисніть «Завантажити», щоб установити (потрібен інтернет)."),
    "Model not installed": (
        "Modellen er ikke installert", "Modellen är inte installerad", "Modellen er ikke installeret",
        "Modell nicht installiert", "Modelo no instalado", "Modèle non installé",
        "Model nie jest zainstalowany", "Модель не встановлено"),
    "The {model} model isn't installed on this computer yet ({size}).\n\n"
    "To use it, click Download under the model list. Or choose a model that's already installed.": (
        "Modellen {model} er ikke installert på denne datamaskinen ennå ({size}).\n\n"
        "For å bruke den, klikk Last ned under modellisten. Eller velg en modell som allerede er installert.",
        "Modellen {model} är inte installerad på den här datorn än ({size}).\n\n"
        "För att använda den klickar du på Ladda ner under modellistan. Eller välj en modell som redan är "
        "installerad.",
        "Modellen {model} er ikke installeret på denne computer endnu ({size}).\n\n"
        "Klik på Hent under modellisten for at bruge den. Eller vælg en model, der allerede er installeret.",
        "Das Modell {model} ist auf diesem Computer noch nicht installiert ({size}).\n\n"
        "Klicken Sie unter der Modellliste auf Herunterladen, um es zu verwenden. Oder wählen Sie ein "
        "bereits installiertes Modell.",
        "El modelo {model} aún no está instalado en este equipo ({size}).\n\n"
        "Para usarlo, haz clic en Descargar debajo de la lista de modelos. O elige un modelo que ya esté "
        "instalado.",
        "Le modèle {model} n'est pas encore installé sur cet ordinateur ({size}).\n\n"
        "Pour l'utiliser, cliquez sur Télécharger sous la liste des modèles. Ou choisissez un modèle déjà "
        "installé.",
        "Model {model} nie jest jeszcze zainstalowany na tym komputerze ({size}).\n\n"
        "Aby go użyć, kliknij Pobierz pod listą modeli. Możesz też wybrać model, który jest już "
        "zainstalowany.",
        "Модель {model} ще не встановлено на цьому комп'ютері ({size}).\n\n"
        "Щоб скористатися нею, натисніть «Завантажити» під списком моделей. Або виберіть модель, яку вже "
        "встановлено."),
    "Not enough disk space": (
        "Ikke nok diskplass", "Inte tillräckligt med diskutrymme", "Ikke nok diskplads",
        "Nicht genügend Speicherplatz", "Espacio en disco insuficiente", "Espace disque insuffisant",
        "Za mało miejsca na dysku", "Недостатньо місця на диску"),
    "The {model} model needs {need}, but only {free} is free on the drive where Whisper keeps its "
    "models:\n\n{folder}\n\nFree up some space or choose a smaller model.": (
        "Modellen {model} trenger {need}, men bare {free} er ledig på disken der Whisper lagrer "
        "modellene sine:\n\n{folder}\n\nFrigjør plass eller velg en mindre modell.",
        "Modellen {model} behöver {need}, men bara {free} är ledigt på disken där Whisper sparar sina "
        "modeller:\n\n{folder}\n\nFrigör utrymme eller välj en mindre modell.",
        "Modellen {model} kræver {need}, men kun {free} er ledig på drevet, hvor Whisper gemmer sine "
        "modeller:\n\n{folder}\n\nFrigør plads, eller vælg en mindre model.",
        "Das Modell {model} benötigt {need}, aber auf dem Laufwerk, auf dem Whisper seine Modelle speichert, "
        "sind nur {free} frei:\n\n{folder}\n\nGeben Sie Speicherplatz frei oder wählen Sie ein kleineres "
        "Modell.",
        "El modelo {model} necesita {need}, pero solo hay {free} libres en la unidad donde Whisper guarda "
        "sus modelos:\n\n{folder}\n\nLibera espacio o elige un modelo más pequeño.",
        "Le modèle {model} nécessite {need}, mais seulement {free} sont libres sur le disque où Whisper "
        "stocke ses modèles :\n\n{folder}\n\nLibérez de l'espace ou choisissez un modèle plus petit.",
        "Model {model} wymaga {need}, a na dysku, na którym Whisper przechowuje modele, wolne jest tylko "
        "{free}:\n\n{folder}\n\nZwolnij miejsce lub wybierz mniejszy model.",
        "Моделі {model} потрібно {need}, але на диску, де Whisper зберігає моделі, вільно лише "
        "{free}:\n\n{folder}\n\nЗвільніть місце або виберіть меншу модель."),
    "Couldn't find the download link. Is openai-whisper installed?": (
        "Fant ikke nedlastingslenken. Er openai-whisper installert?",
        "Hittade inte nedladdningslänken. Är openai-whisper installerat?",
        "Kunne ikke finde downloadlinket. Er openai-whisper installeret?",
        "Download-Link nicht gefunden. Ist openai-whisper installiert?",
        "No se encontró el enlace de descarga. ¿Está instalado openai-whisper?",
        "Lien de téléchargement introuvable. openai-whisper est-il installé ?",
        "Nie znaleziono linku do pobrania. Czy openai-whisper jest zainstalowany?",
        "Не вдалося знайти посилання для завантаження. Чи встановлено openai-whisper?"),
    "The downloaded file is damaged (checksum mismatch). Please try again.": (
        "Den nedlastede filen er skadet (sjekksummen stemmer ikke). Prøv igjen.",
        "Den nedladdade filen är skadad (kontrollsumman stämmer inte). Försök igen.",
        "Den hentede fil er beskadiget (kontrolsummen passer ikke). Prøv igen.",
        "Die heruntergeladene Datei ist beschädigt (Prüfsumme stimmt nicht). Bitte versuchen Sie es erneut.",
        "El archivo descargado está dañado (la suma de comprobación no coincide). Inténtalo de nuevo.",
        "Le fichier téléchargé est endommagé (somme de contrôle incorrecte). Veuillez réessayer.",
        "Pobrany plik jest uszkodzony (niezgodna suma kontrolna). Spróbuj ponownie.",
        "Завантажений файл пошкоджено (контрольна сума не збігається). Спробуйте ще раз."),

    # transcription language
    "Language": ("Språk", "Språk", "Sprog", "Sprache", "Idioma", "Langue", "Język", "Мова"),
    "Auto detects from the first 30 seconds": (
        "Auto gjenkjenner språket fra de første 30 sekundene",
        "Auto känner igen språket från de första 30 sekunderna",
        "Auto genkender sproget ud fra de første 30 sekunder",
        "Auto erkennt die Sprache anhand der ersten 30 Sekunden",
        "Auto lo detecta en los primeros 30 segundos",
        "Auto la détecte dans les 30 premières secondes",
        "Auto rozpoznaje język z pierwszych 30 sekund",
        "Авто визначає мову за першими 30 секундами"),
    "Auto": ("Auto", "Auto", "Auto", "Auto", "Auto", "Auto", "Auto", "Авто"),
    "English": (
        "Engelsk", "Engelska", "Engelsk", "Englisch", "Inglés", "Anglais", "Angielski", "Англійська"),
    "Norwegian": (
        "Norsk", "Norska", "Norsk", "Norwegisch", "Noruego", "Norvégien", "Norweski", "Норвезька"),
    "Swedish": ("Svensk", "Svenska", "Svensk", "Schwedisch", "Sueco", "Suédois", "Szwedzki", "Шведська"),
    "Danish": ("Dansk", "Danska", "Dansk", "Dänisch", "Danés", "Danois", "Duński", "Данська"),
    "German": ("Tysk", "Tyska", "Tysk", "Deutsch", "Alemán", "Allemand", "Niemiecki", "Німецька"),
    "More ▾": ("Flere ▾", "Fler ▾", "Flere ▾", "Mehr ▾", "Más ▾", "Plus ▾", "Więcej ▾", "Більше ▾"),
    "Arabic": ("Arabisk", "Arabiska", "Arabisk", "Arabisch", "Árabe", "Arabe", "Arabski", "Арабська"),
    "Chinese": ("Kinesisk", "Kinesiska", "Kinesisk", "Chinesisch", "Chino", "Chinois", "Chiński", "Китайська"),
    "Dutch": (
        "Nederlandsk", "Nederländska", "Nederlandsk", "Niederländisch", "Neerlandés", "Néerlandais",
        "Niderlandzki", "Нідерландська"),
    "Finnish": ("Finsk", "Finska", "Finsk", "Finnisch", "Finés", "Finnois", "Fiński", "Фінська"),
    "French": ("Fransk", "Franska", "Fransk", "Französisch", "Francés", "Français", "Francuski", "Французька"),
    "Hindi": ("Hindi", "Hindi", "Hindi", "Hindi", "Hindi", "Hindi", "Hindi", "Гінді"),
    "Italian": (
        "Italiensk", "Italienska", "Italiensk", "Italienisch", "Italiano", "Italien", "Włoski", "Італійська"),
    "Japanese": ("Japansk", "Japanska", "Japansk", "Japanisch", "Japonés", "Japonais", "Japoński", "Японська"),
    "Korean": ("Koreansk", "Koreanska", "Koreansk", "Koreanisch", "Coreano", "Coréen", "Koreański", "Корейська"),
    "Persian": ("Persisk", "Persiska", "Persisk", "Persisch", "Persa", "Persan", "Perski", "Перська"),
    "Polish": ("Polsk", "Polska", "Polsk", "Polnisch", "Polaco", "Polonais", "Polski", "Польська"),
    "Portuguese": (
        "Portugisisk", "Portugisiska", "Portugisisk", "Portugiesisch", "Portugués", "Portugais", "Portugalski",
        "Португальська"),
    "Russian": ("Russisk", "Ryska", "Russisk", "Russisch", "Ruso", "Russe", "Rosyjski", "Російська"),
    "Spanish": ("Spansk", "Spanska", "Spansk", "Spanisch", "Español", "Espagnol", "Hiszpański", "Іспанська"),
    "Turkish": ("Tyrkisk", "Turkiska", "Tyrkisk", "Türkisch", "Turco", "Turc", "Turecki", "Турецька"),
    "Ukrainian": (
        "Ukrainsk", "Ukrainska", "Ukrainsk", "Ukrainisch", "Ucraniano", "Ukrainien", "Ukraiński", "Українська"),

    # actions and progress
    "Start transcribing": (
        "Start transkribering", "Starta transkribering", "Start transskribering", "Transkription starten",
        "Empezar a transcribir", "Lancer la transcription", "Rozpocznij transkrypcję", "Почати транскрибування"),
    "Pause": ("Pause", "Pausa", "Pause", "Pause", "Pausar", "Pause", "Wstrzymaj", "Пауза"),
    "Resume": ("Fortsett", "Fortsätt", "Fortsæt", "Fortsetzen", "Reanudar", "Reprendre", "Wznów", "Продовжити"),
    "Cancel": ("Avbryt", "Avbryt", "Annuller", "Abbrechen", "Cancelar", "Annuler", "Anuluj", "Скасувати"),
    "Ready": ("Klar", "Redo", "Klar", "Bereit", "Listo", "Prêt", "Gotowe", "Готово"),
    "Pick a file to start": (
        "Velg en fil for å starte", "Välj en fil för att börja", "Vælg en fil for at begynde",
        "Wählen Sie eine Datei, um zu beginnen", "Elige un archivo para empezar",
        "Choisissez un fichier pour commencer", "Wybierz plik, aby rozpocząć", "Виберіть файл, щоб почати"),
    "Transcript": (
        "Transkripsjon", "Transkription", "Transskription", "Transkript",
        "Transcripción", "Transcription", "Transkrypcja", "Транскрипт"),
    "Log": ("Logg", "Logg", "Log", "Protokoll", "Registro", "Journal", "Dziennik", "Журнал"),
    "Open folder": (
        "Åpne mappe", "Öppna mapp", "Åbn mappe", "Ordner öffnen",
        "Abrir carpeta", "Ouvrir le dossier", "Otwórz folder", "Відкрити папку"),
    "Copy": ("Kopier", "Kopiera", "Kopiér", "Kopieren", "Copiar", "Copier", "Kopiuj", "Копіювати"),
    "Copied ✓": (
        "Kopiert ✓", "Kopierat ✓", "Kopieret ✓", "Kopiert ✓",
        "Copiado ✓", "Copié ✓", "Skopiowano ✓", "Скопійовано ✓"),
    "The transcript appears here while Whisper works through the audio.": (
        "Transkripsjonen vises her mens Whisper jobber seg gjennom lyden.",
        "Transkriptionen visas här medan Whisper arbetar sig igenom ljudet.",
        "Transskriptionen vises her, mens Whisper arbejder sig gennem lyden.",
        "Das Transkript erscheint hier, während Whisper das Audio verarbeitet.",
        "La transcripción aparece aquí mientras Whisper procesa el audio.",
        "La transcription s'affiche ici pendant que Whisper traite l'audio.",
        "Transkrypcja pojawi się tutaj, gdy Whisper będzie przetwarzać nagranie.",
        "Транскрипт з'являтиметься тут, поки Whisper обробляє аудіо."),
    "Waiting for the first words…": (
        "Venter på de første ordene…", "Väntar på de första orden…", "Venter på de første ord…",
        "Warten auf die ersten Wörter…", "Esperando las primeras palabras…", "En attente des premiers mots…",
        "Oczekiwanie na pierwsze słowa…", "Очікування перших слів…"),
    "(Whisper found no speech in this file.)": (
        "(Whisper fant ingen tale i denne filen.)",
        "(Whisper hittade inget tal i filen.)",
        "(Whisper fandt ingen tale i filen.)",
        "(Whisper hat in dieser Datei keine Sprache gefunden.)",
        "(Whisper no encontró voz en este archivo.)",
        "(Whisper n'a trouvé aucune parole dans ce fichier.)",
        "(Whisper nie znalazł mowy w tym pliku.)",
        "(Whisper не знайшов мовлення в цьому файлі.)"),
    "Couldn't start Whisper": (
        "Kunne ikke starte Whisper", "Kunde inte starta Whisper", "Kunne ikke starte Whisper",
        "Whisper konnte nicht gestartet werden", "No se pudo iniciar Whisper", "Impossible de lancer Whisper",
        "Nie udało się uruchomić Whisper", "Не вдалося запустити Whisper"),
    "Loading model": (
        "Laster modell", "Laddar modell", "Indlæser model", "Modell wird geladen",
        "Cargando modelo", "Chargement du modèle", "Ładowanie modelu", "Завантаження моделі"),
    "{model} · auto-detect language": (
        "{model} · gjenkjenn språk automatisk", "{model} · identifiera språk automatiskt",
        "{model} · genkend sprog automatisk", "{model} · Sprache automatisch erkennen",
        "{model} · detección automática del idioma", "{model} · détection automatique de la langue",
        "{model} · automatyczne rozpoznawanie języka", "{model} · автоматичне визначення мови"),
    "Downloading the {model} model": (
        "Laster ned modellen {model}", "Laddar ner modellen {model}", "Henter modellen {model}",
        "Modell {model} wird heruntergeladen", "Descargando el modelo {model}",
        "Téléchargement du modèle {model}", "Pobieranie modelu {model}", "Завантаження моделі {model}"),
    "Connecting…": (
        "Kobler til…", "Ansluter…", "Opretter forbindelse…", "Verbindung wird hergestellt…",
        "Conectando…", "Connexion…", "Łączenie…", "Підключення…"),
    "{done} of {total} · {speed}/s": (
        "{done} av {total} · {speed}/s", "{done} av {total} · {speed}/s", "{done} af {total} · {speed}/s",
        "{done} von {total} · {speed}/s", "{done} de {total} · {speed}/s", "{done} sur {total} · {speed}/s",
        "{done} z {total} · {speed}/s", "{done} з {total} · {speed}/s"),
    "Model downloaded": (
        "Modellen er lastet ned", "Modellen har laddats ner", "Modellen er hentet", "Modell heruntergeladen",
        "Modelo descargado", "Modèle téléchargé", "Model pobrany", "Модель завантажено"),
    "{model} is ready": (
        "{model} er klar", "{model} är redo", "{model} er klar", "{model} ist bereit",
        "{model} está listo", "{model} est prêt", "{model} jest gotowy", "{model} готова"),
    "Download cancelled": (
        "Nedlastingen ble avbrutt", "Nedladdningen avbröts", "Hentningen blev annulleret",
        "Download abgebrochen", "Descarga cancelada", "Téléchargement annulé", "Pobieranie anulowane",
        "Завантаження скасовано"),
    "{model} wasn't downloaded": (
        "{model} ble ikke lastet ned", "{model} laddades inte ner", "{model} blev ikke hentet",
        "{model} wurde nicht heruntergeladen", "{model} no se descargó", "{model} n'a pas été téléchargé",
        "Model {model} nie został pobrany", "{model} не завантажено"),
    "Download failed": (
        "Nedlastingen mislyktes", "Nedladdningen misslyckades", "Hentningen mislykkedes",
        "Download fehlgeschlagen", "Error en la descarga", "Échec du téléchargement",
        "Pobieranie nie powiodło się", "Не вдалося завантажити"),
    "Transcribing": (
        "Transkriberer", "Transkriberar", "Transskriberer", "Transkription läuft",
        "Transcribiendo", "Transcription en cours", "Transkrypcja w toku", "Транскрибування"),
    "Audio length unknown, showing time transcribed": (
        "Ukjent lydlengde, viser transkribert tid",
        "Okänd ljudlängd, visar transkriberad tid",
        "Ukendt lydlængde, viser transskriberet tid",
        "Audiolänge unbekannt, angezeigt wird die transkribierte Zeit",
        "Duración desconocida; se muestra el tiempo transcrito",
        "Durée inconnue, affichage du temps transcrit",
        "Nieznana długość nagrania, pokazywany jest czas transkrypcji",
        "Тривалість невідома, показано транскрибований час"),
    "Downloading model (first use only)": (
        "Laster ned modell (kun første gang)", "Laddar ner modell (endast första gången)",
        "Henter model (kun første gang)", "Modell wird heruntergeladen (nur beim ersten Mal)",
        "Descargando modelo (solo la primera vez)", "Téléchargement du modèle (première utilisation uniquement)",
        "Pobieranie modelu (tylko za pierwszym razem)", "Завантаження моделі (лише вперше)"),
    "Detecting language": (
        "Gjenkjenner språk", "Identifierar språk", "Genkender sprog", "Sprache wird erkannt",
        "Detectando idioma", "Détection de la langue", "Rozpoznawanie języka", "Визначення мови"),
    "Cancelled": (
        "Avbrutt", "Avbrutet", "Annulleret", "Abgebrochen", "Cancelado", "Annulé", "Anulowano", "Скасовано"),
    "Whisper was stopped": (
        "Whisper ble stoppet", "Whisper stoppades", "Whisper blev stoppet", "Whisper wurde gestoppt",
        "Whisper se detuvo", "Whisper a été arrêté", "Whisper został zatrzymany", "Whisper зупинено"),
    "Done": ("Ferdig", "Klart", "Færdig", "Fertig", "Completado", "Terminé", "Ukończono", "Завершено"),
    "Saved as {name} next to the audio file": (
        "Lagret som {name} ved siden av lydfilen", "Sparad som {name} bredvid ljudfilen",
        "Gemt som {name} ved siden af lydfilen", "Gespeichert als {name} neben der Audiodatei",
        "Guardado como {name} junto al archivo de audio", "Enregistré sous {name} à côté du fichier audio",
        "Zapisano jako {name} obok pliku audio", "Збережено як {name} поруч з аудіофайлом"),
    "Failed": (
        "Mislyktes", "Misslyckades", "Mislykkedes", "Fehlgeschlagen", "Error", "Échec", "Niepowodzenie",
        "Помилка"),
    "Exit code {rc}": (
        "Avslutningskode {rc}", "Slutkod {rc}", "Afslutningskode {rc}", "Exitcode {rc}",
        "Código de salida {rc}", "Code de sortie {rc}", "Kod wyjścia {rc}", "Код виходу {rc}"),
    "Cancelling…": (
        "Avbryter…", "Avbryter…", "Annullerer…", "Wird abgebrochen…",
        "Cancelando…", "Annulation…", "Anulowanie…", "Скасування…"),
    "Couldn't pause Whisper": (
        "Kunne ikke sette Whisper på pause", "Kunde inte pausa Whisper", "Kunne ikke sætte Whisper på pause",
        "Whisper konnte nicht angehalten werden", "No se pudo pausar Whisper",
        "Impossible de mettre Whisper en pause", "Nie udało się wstrzymać Whisper",
        "Не вдалося призупинити Whisper"),
    "Couldn't resume Whisper": (
        "Kunne ikke fortsette Whisper", "Kunde inte återuppta Whisper", "Kunne ikke fortsætte Whisper",
        "Whisper konnte nicht fortgesetzt werden", "No se pudo reanudar Whisper",
        "Impossible de reprendre Whisper", "Nie udało się wznowić Whisper", "Не вдалося продовжити Whisper"),
    "Paused": (
        "Pauset", "Pausad", "På pause", "Angehalten", "En pausa", "En pause", "Wstrzymano", "Призупинено"),
    "Click Resume to continue where it stopped": (
        "Klikk Fortsett for å fortsette der den stoppet",
        "Klicka på Fortsätt för att fortsätta där det slutade",
        "Klik på Fortsæt for at fortsætte, hvor den stoppede",
        "Klicken Sie auf Fortsetzen, um an derselben Stelle weiterzumachen",
        "Haz clic en Reanudar para continuar donde se detuvo",
        "Cliquez sur Reprendre pour continuer là où il s'est arrêté",
        "Kliknij Wznów, aby kontynuować od miejsca zatrzymania",
        "Натисніть «Продовжити», щоб продовжити з місця зупинки"),

    # session panel
    "Session": ("Økt", "Session", "Session", "Sitzung", "Sesión", "Session", "Sesja", "Сеанс"),
    "Live stats for the current run": (
        "Direkte statistikk for gjeldende kjøring", "Livestatistik för den aktuella körningen",
        "Live-statistik for den aktuelle kørsel", "Live-Statistik für den aktuellen Durchlauf",
        "Estadísticas en directo de la ejecución actual", "Statistiques en direct de l'exécution en cours",
        "Statystyki na żywo bieżącego przebiegu", "Статистика поточного запуску наживо"),
    "Elapsed": (
        "Medgått tid", "Förfluten tid", "Forløbet tid", "Verstrichen",
        "Transcurrido", "Écoulé", "Upłynęło", "Минуло"),
    "since start": (
        "siden start", "sedan start", "siden start", "seit dem Start",
        "desde el inicio", "depuis le début", "od startu", "від початку"),
    "Time left": (
        "Tid igjen", "Tid kvar", "Tid tilbage", "Verbleibend",
        "Tiempo restante", "Temps restant", "Pozostało", "Залишилось"),
    "estimate": (
        "anslag", "uppskattning", "skøn", "Schätzung", "estimación", "estimation", "szacunkowo", "оцінка"),
    "Finishes at": (
        "Ferdig kl.", "Klar kl.", "Færdig kl.", "Fertig um",
        "Termina a las", "Fin prévue à", "Koniec o", "Завершиться о"),
    "local time": (
        "lokal tid", "lokal tid", "lokal tid", "Ortszeit", "hora local", "heure locale", "czas lokalny",
        "місцевий час"),
    "Speed": (
        "Hastighet", "Hastighet", "Hastighed", "Geschwindigkeit", "Velocidad", "Vitesse", "Szybkość",
        "Швидкість"),
    "audio time per second": (
        "lydtid per sekund", "ljudtid per sekund", "lydtid pr. sekund", "Audiozeit pro Sekunde",
        "tiempo de audio por segundo", "temps audio par seconde", "czas nagrania na sekundę",
        "час аудіо за секунду"),
    "CPU use": (
        "CPU-bruk", "CPU-användning", "CPU-forbrug", "CPU-Auslastung",
        "Uso de CPU", "Utilisation CPU", "Użycie CPU", "Використання ЦП"),
    "Whisper, of the whole CPU": (
        "Whisper, av hele CPU-en", "Whisper, av hela processorn", "Whisper, af hele CPU'en",
        "Whisper, der gesamten CPU", "Whisper, de toda la CPU", "Whisper, sur tout le processeur",
        "Whisper, całego procesora", "Whisper, від усього ЦП"),
    "Memory use": (
        "Minnebruk", "Minnesanvändning", "Hukommelsesforbrug", "Speichernutzung",
        "Uso de memoria", "Mémoire utilisée", "Użycie pamięci", "Використання пам'яті"),
    "Whisper, of {gb} GB": (
        "Whisper, av {gb} GB", "Whisper, av {gb} GB", "Whisper, af {gb} GB", "Whisper, von {gb} GB",
        "Whisper, de {gb} GB", "Whisper, sur {gb} GB", "Whisper, z {gb} GB", "Whisper, з {gb} GB"),

    # system
    "Your system": (
        "Ditt system", "Ditt system", "Dit system", "Ihr System",
        "Tu sistema", "Votre système", "Twój system", "Ваша система"),
    "Operating system": (
        "Operativsystem", "Operativsystem", "Styresystem", "Betriebssystem",
        "Sistema operativo", "Système d'exploitation", "System operacyjny", "Операційна система"),
    "Processor": (
        "Prosessor", "Processor", "Processor", "Prozessor", "Procesador", "Processeur", "Procesor", "Процесор"),
    "Threads": ("Tråder", "Trådar", "Tråde", "Threads", "Hilos", "Threads", "Wątki", "Потоки"),
    "Memory": (
        "Minne", "Minne", "Hukommelse", "Arbeitsspeicher", "Memoria", "Mémoire", "Pamięć", "Пам'ять"),
    "Graphics": (
        "Grafikk", "Grafik", "Grafik", "Grafik", "Gráficos", "Graphique", "Grafika", "Графіка"),
    "None found": (
        "Ingen funnet", "Inga hittades", "Ingen fundet", "Keine gefunden",
        "No se encontró ninguna", "Aucune trouvée", "Nie znaleziono", "Не знайдено"),
    "Whisper on GPU": (
        "Whisper på GPU", "Whisper på GPU", "Whisper på GPU", "Whisper auf GPU",
        "Whisper en GPU", "Whisper sur GPU", "Whisper na GPU", "Whisper на GPU"),
    "Yes · CUDA": (
        "Ja · CUDA", "Ja · CUDA", "Ja · CUDA", "Ja · CUDA", "Sí · CUDA", "Oui · CUDA", "Tak · CUDA", "Так · CUDA"),
    "No · CPU only": (
        "Nei · kun CPU", "Nej · endast CPU", "Nej · kun CPU", "Nein · nur CPU",
        "No · solo CPU", "Non · CPU uniquement", "Nie · tylko CPU", "Ні · лише ЦП"),
    "torch is not installed.": (
        "torch er ikke installert.", "torch är inte installerat.", "torch er ikke installeret.",
        "torch ist nicht installiert.", "torch no está instalado.", "torch n'est pas installé.",
        "torch nie jest zainstalowany.", "torch не встановлено."),
    "The installed torch is a CPU-only build, so your NVIDIA card can't be used. "
    "See Requirements for the CUDA install command.": (
        "Den installerte torch-versjonen støtter bare CPU, så NVIDIA-kortet ditt kan ikke brukes. "
        "Se Krav for kommandoen som installerer CUDA-versjonen.",
        "Det installerade torch är en version endast för CPU, så ditt NVIDIA-kort kan inte användas. "
        "Se Krav för kommandot som installerar CUDA-versionen.",
        "Den installerede torch er en version kun til CPU, så dit NVIDIA-kort kan ikke bruges. "
        "Se Krav for kommandoen, der installerer CUDA-versionen.",
        "Das installierte torch ist eine reine CPU-Version, daher kann Ihre NVIDIA-Karte nicht genutzt "
        "werden. Den Befehl für die CUDA-Version finden Sie unter Voraussetzungen.",
        "El torch instalado es una versión solo para CPU, así que no se puede usar tu tarjeta NVIDIA. "
        "Consulta Requisitos para ver el comando que instala la versión con CUDA.",
        "Le torch installé est une version CPU uniquement : votre carte NVIDIA ne peut donc pas être "
        "utilisée. Consultez Prérequis pour la commande qui installe la version CUDA.",
        "Zainstalowany torch to wersja tylko dla CPU, więc karta NVIDIA nie może być używana. "
        "Polecenie instalujące wersję CUDA znajdziesz w sekcji Wymagania.",
        "Встановлений torch — версія лише для ЦП, тому вашу відеокарту NVIDIA не можна використати. "
        "Команду для встановлення версії з CUDA дивіться в розділі «Вимоги»."),
    "torch has CUDA support but can't reach the card. Check the NVIDIA driver.": (
        "torch har CUDA-støtte, men får ikke kontakt med kortet. Sjekk NVIDIA-driveren.",
        "torch har CUDA-stöd men når inte kortet. Kontrollera NVIDIA-drivrutinen.",
        "torch har CUDA-understøttelse, men kan ikke nå kortet. Kontrollér NVIDIA-driveren.",
        "torch unterstützt CUDA, erreicht die Karte aber nicht. Prüfen Sie den NVIDIA-Treiber.",
        "torch es compatible con CUDA, pero no puede acceder a la tarjeta. Revisa el controlador de NVIDIA.",
        "torch prend en charge CUDA mais n'accède pas à la carte. Vérifiez le pilote NVIDIA.",
        "torch obsługuje CUDA, ale nie może połączyć się z kartą. Sprawdź sterownik NVIDIA.",
        "torch підтримує CUDA, але не може звернутися до відеокарти. Перевірте драйвер NVIDIA."),
    "Checking GPU…": (
        "Sjekker GPU…", "Kontrollerar GPU…", "Kontrollerer GPU…", "GPU wird geprüft…",
        "Comprobando GPU…", "Vérification du GPU…", "Sprawdzanie GPU…", "Перевірка GPU…"),
    "Suggested model": (
        "Anbefalt modell", "Rekommenderad modell", "Anbefalet model", "Empfohlenes Modell",
        "Modelo recomendado", "Modèle recommandé", "Zalecany model", "Рекомендована модель"),
    "CPU · {threads} threads · {model}": (
        "CPU · {threads} tråder · {model}", "CPU · {threads} trådar · {model}",
        "CPU · {threads} tråde · {model}", "CPU · {threads} Threads · {model}",
        "CPU · {threads} hilos · {model}", "CPU · {threads} threads · {model}",
        "CPU · wątki: {threads} · {model}", "ЦП · потоків: {threads} · {model}"),
    "CPU only": (
        "Kun CPU", "Endast CPU", "Kun CPU", "Nur CPU", "Solo CPU", "CPU uniquement", "Tylko CPU", "Лише ЦП"),

    # requirements
    "Requirements": (
        "Krav", "Krav", "Krav", "Voraussetzungen", "Requisitos", "Prérequis", "Wymagania", "Вимоги"),
    "Python comes with your Linux distribution; its package manager keeps it updated.": (
        "Python følger med Linux-distribusjonen din; pakkebehandleren holder den oppdatert.",
        "Python följer med din Linux-distribution; dess pakethanterare håller det uppdaterat.",
        "Python følger med din Linux-distribution; dens pakkehåndtering holder det opdateret.",
        "Python gehört zu Ihrer Linux-Distribution; deren Paketverwaltung hält es aktuell.",
        "Python viene con tu distribución de Linux; su gestor de paquetes lo mantiene actualizado.",
        "Python est fourni avec votre distribution Linux ; son gestionnaire de paquets le tient à jour.",
        "Python jest częścią dystrybucji Linuksa; menedżer pakietów dba o jego aktualizacje.",
        "Python постачається з вашим дистрибутивом Linux; його менеджер пакетів оновлює Python."),
    "{same} is the latest {cycle} release.": (
        "{same} er den nyeste {cycle}-utgaven.", "{same} är den senaste {cycle}-versionen.",
        "{same} er den nyeste {cycle}-udgave.", "{same} ist die neueste {cycle}-Version.",
        "{same} es la última versión de {cycle}.", "{same} est la dernière version {cycle}.",
        "{same} to najnowsze wydanie {cycle}.", "{same} — найновіший випуск {cycle}."),
    "{same} is the latest {cycle} release. Get it from python.org.": (
        "{same} er den nyeste {cycle}-utgaven. Last den ned fra python.org.",
        "{same} är den senaste {cycle}-versionen. Hämta den från python.org.",
        "{same} er den nyeste {cycle}-udgave. Hent den fra python.org.",
        "{same} ist die neueste {cycle}-Version. Laden Sie sie von python.org herunter.",
        "{same} es la última versión de {cycle}. Descárgala de python.org.",
        "{same} est la dernière version {cycle}. Téléchargez-la sur python.org.",
        "{same} to najnowsze wydanie {cycle}. Pobierz je z python.org.",
        "{same} — найновіший випуск {cycle}. Завантажте його з python.org."),
    "Python {version} is a separate install; Whisper and torch would need installing there again.": (
        "Python {version} er en separat installasjon; Whisper og torch må da installeres der på nytt.",
        "Python {version} är en separat installation; Whisper och torch måste då installeras där igen.",
        "Python {version} er en separat installation; Whisper og torch skal så installeres der igen.",
        "Python {version} ist eine separate Installation; Whisper und torch müssten dort erneut installiert "
        "werden.",
        "Python {version} es una instalación aparte; habría que volver a instalar Whisper y torch en ella.",
        "Python {version} est une installation distincte ; il faudrait y réinstaller Whisper et torch.",
        "Python {version} to osobna instalacja; Whisper i torch trzeba by w niej zainstalować ponownie.",
        "Python {version} — окреме встановлення; Whisper і torch довелося б установити там заново."),
    "Needs Homebrew first: see brew.sh.": (
        "Krever Homebrew først: se brew.sh.", "Kräver Homebrew först: se brew.sh.",
        "Kræver Homebrew først: se brew.sh.", "Benötigt zuerst Homebrew: siehe brew.sh.",
        "Necesita Homebrew primero: consulta brew.sh.", "Nécessite d'abord Homebrew : voir brew.sh.",
        "Najpierw wymaga Homebrew: zobacz brew.sh.", "Спершу потрібен Homebrew: див. brew.sh."),
    "FFmpeg comes from RPM Fusion: enable it first (rpmfusion.org).": (
        "FFmpeg kommer fra RPM Fusion: aktiver det først (rpmfusion.org).",
        "FFmpeg kommer från RPM Fusion: aktivera det först (rpmfusion.org).",
        "FFmpeg kommer fra RPM Fusion: aktivér det først (rpmfusion.org).",
        "FFmpeg stammt aus RPM Fusion: Aktivieren Sie es zuerst (rpmfusion.org).",
        "FFmpeg viene de RPM Fusion: actívalo primero (rpmfusion.org).",
        "FFmpeg provient de RPM Fusion : activez-le d'abord (rpmfusion.org).",
        "FFmpeg pochodzi z RPM Fusion: najpierw je włącz (rpmfusion.org).",
        "FFmpeg постачається з RPM Fusion: спершу увімкніть його (rpmfusion.org)."),
    "Install ffmpeg with your distribution's package manager.": (
        "Installer ffmpeg med pakkebehandleren til distribusjonen din.",
        "Installera ffmpeg med din distributions pakethanterare.",
        "Installér ffmpeg med din distributions pakkehåndtering.",
        "Installieren Sie ffmpeg mit der Paketverwaltung Ihrer Distribution.",
        "Instala ffmpeg con el gestor de paquetes de tu distribución.",
        "Installez ffmpeg avec le gestionnaire de paquets de votre distribution.",
        "Zainstaluj ffmpeg menedżerem pakietów swojej dystrybucji.",
        "Установіть ffmpeg менеджером пакетів вашого дистрибутива."),
    "Your distribution's FFmpeg works fine with Whisper.": (
        "FFmpeg fra distribusjonen din fungerer fint med Whisper.",
        "Din distributions FFmpeg fungerar bra med Whisper.",
        "Din distributions FFmpeg fungerer fint med Whisper.",
        "Das FFmpeg Ihrer Distribution funktioniert gut mit Whisper.",
        "El FFmpeg de tu distribución funciona bien con Whisper.",
        "Le FFmpeg de votre distribution fonctionne bien avec Whisper.",
        "FFmpeg z Twojej dystrybucji dobrze działa z Whisper.",
        "FFmpeg з вашого дистрибутива добре працює з Whisper."),
    "tkinterdnd2 (optional)": (
        "tkinterdnd2 (valgfri)", "tkinterdnd2 (valfritt)", "tkinterdnd2 (valgfri)", "tkinterdnd2 (optional)",
        "tkinterdnd2 (opcional)", "tkinterdnd2 (facultatif)", "tkinterdnd2 (opcjonalnie)",
        "tkinterdnd2 (необов'язково)"),
    "Lets you drop files onto the window. Restart the app after installing it.": (
        "Lar deg slippe filer på vinduet. Start appen på nytt etter at den er installert.",
        "Låter dig släppa filer på fönstret. Starta om appen efter installationen.",
        "Lader dig slippe filer på vinduet. Genstart appen efter installationen.",
        "Ermöglicht das Ablegen von Dateien im Fenster. Starten Sie die App nach der Installation neu.",
        "Te permite soltar archivos en la ventana. Reinicia la aplicación después de instalarlo.",
        "Permet de déposer des fichiers dans la fenêtre. Redémarrez l'application après l'installation.",
        "Pozwala upuszczać pliki na okno. Po instalacji uruchom aplikację ponownie.",
        "Дає змогу перетягувати файли у вікно. Після встановлення перезапустіть застосунок."),
    "Installed, but drag-and-drop didn't start. If you just installed it, restart the app.": (
        "Installert, men dra-og-slipp startet ikke. Hvis du nettopp installerte den, start appen på nytt.",
        "Installerat, men dra och släpp startade inte. Om du nyss installerade det, starta om appen.",
        "Installeret, men træk og slip startede ikke. Hvis du lige har installeret det, så genstart appen.",
        "Installiert, aber Drag-and-drop wurde nicht gestartet. Wenn Sie es gerade installiert haben, "
        "starten Sie die App neu.",
        "Instalado, pero arrastrar y soltar no se inició. Si acabas de instalarlo, reinicia la aplicación.",
        "Installé, mais le glisser-déposer n'a pas démarré. Si vous venez de l'installer, redémarrez "
        "l'application.",
        "Zainstalowano, ale przeciąganie i upuszczanie nie uruchomiło się. Jeśli właśnie go zainstalowano, "
        "uruchom aplikację ponownie.",
        "Встановлено, але перетягування не запустилося. Якщо ви щойно встановили його, перезапустіть "
        "застосунок."),
    "CPU-only build. Install the CUDA build to use your NVIDIA card.": (
        "Versjon kun for CPU. Installer CUDA-versjonen for å bruke NVIDIA-kortet ditt.",
        "Version endast för CPU. Installera CUDA-versionen för att använda ditt NVIDIA-kort.",
        "Version kun til CPU. Installér CUDA-versionen for at bruge dit NVIDIA-kort.",
        "Reine CPU-Version. Installieren Sie die CUDA-Version, um Ihre NVIDIA-Karte zu nutzen.",
        "Versión solo para CPU. Instala la versión con CUDA para usar tu tarjeta NVIDIA.",
        "Version CPU uniquement. Installez la version CUDA pour utiliser votre carte NVIDIA.",
        "Wersja tylko dla CPU. Zainstaluj wersję CUDA, aby używać karty NVIDIA.",
        "Версія лише для ЦП. Установіть версію з CUDA, щоб використовувати відеокарту NVIDIA."),
    "Up to date": (
        "Oppdatert", "Uppdaterad", "Opdateret", "Aktuell", "Actualizado", "À jour", "Aktualny", "Актуально"),
    "Update": (
        "Oppdater", "Uppdatera", "Opdatér", "Aktualisieren", "Actualizar", "Mettre à jour", "Aktualizuj",
        "Оновити"),
    "Missing": ("Mangler", "Saknas", "Mangler", "Fehlt", "Falta", "Manquant", "Brak", "Відсутній"),
    "CPU build": (
        "CPU-versjon", "CPU-version", "CPU-version", "CPU-Version",
        "Versión CPU", "Version CPU", "Wersja CPU", "Версія для ЦП"),
    "Couldn't check": (
        "Kunne ikke sjekke", "Kunde inte kontrollera", "Kunne ikke kontrollere", "Prüfung nicht möglich",
        "No se pudo comprobar", "Vérification impossible", "Nie sprawdzono", "Не вдалося перевірити"),
    "Optional": (
        "Valgfri", "Valfritt", "Valgfri", "Optional", "Opcional", "Facultatif", "Opcjonalne", "Необов'язково"),
    "Commands for {os}": (
        "Kommandoer for {os}", "Kommandon för {os}", "Kommandoer til {os}", "Befehle für {os}",
        "Comandos para {os}", "Commandes pour {os}", "Polecenia dla {os}", "Команди для {os}"),
    "Installed {version}": (
        "Installert {version}", "Installerad {version}", "Installeret {version}", "Installiert {version}",
        "Instalado {version}", "Installé {version}", "Zainstalowano {version}", "Встановлено {version}"),
    "Not installed": (
        "Ikke installert", "Inte installerad", "Ikke installeret", "Nicht installiert",
        "No instalado", "Non installé", "Nie zainstalowano", "Не встановлено"),
    "Latest {version}": (
        "Nyeste {version}", "Senaste {version}", "Nyeste {version}", "Neueste {version}",
        "Última {version}", "Dernière {version}", "Najnowsza {version}", "Найновіша {version}"),
    "Click a command to copy it, then paste it in a terminal.": (
        "Klikk på en kommando for å kopiere den, og lim den inn i en terminal.",
        "Klicka på ett kommando för att kopiera det och klistra sedan in det i en terminal.",
        "Klik på en kommando for at kopiere den, og indsæt den derefter i en terminal.",
        "Klicken Sie auf einen Befehl, um ihn zu kopieren, und fügen Sie ihn in ein Terminal ein.",
        "Haz clic en un comando para copiarlo y pégalo en una terminal.",
        "Cliquez sur une commande pour la copier, puis collez-la dans un terminal.",
        "Kliknij polecenie, aby je skopiować, a potem wklej je w terminalu.",
        "Натисніть команду, щоб скопіювати її, а потім вставте в термінал."),
    "{n} missing": (
        "{n} mangler", "{n} saknas", "{n} mangler", "Fehlend: {n}",
        "Faltan: {n}", "Manquants : {n}", "Brakujące: {n}", "Відсутні: {n}"),
    "1 update available": (
        "1 oppdatering tilgjengelig", "1 uppdatering tillgänglig", "1 opdatering tilgængelig",
        "1 Update verfügbar", "1 actualización disponible", "1 mise à jour disponible",
        "Dostępne aktualizacje: 1", "Доступні оновлення: 1"),
    "{n} updates available": (
        "{n} oppdateringer tilgjengelig", "{n} uppdateringar tillgängliga", "{n} opdateringer tilgængelige",
        "{n} Updates verfügbar", "{n} actualizaciones disponibles", "{n} mises à jour disponibles",
        "Dostępne aktualizacje: {n}", "Доступні оновлення: {n}"),
    "Installed · couldn't check online": (
        "Installert · kunne ikke sjekke på nett", "Installerat · kunde inte kontrollera online",
        "Installeret · kunne ikke kontrollere online", "Installiert · Online-Prüfung nicht möglich",
        "Instalado · no se pudo comprobar en línea", "Installé · vérification en ligne impossible",
        "Zainstalowano · nie udało się sprawdzić online", "Встановлено · не вдалося перевірити онлайн"),
    "All up to date": (
        "Alt er oppdatert", "Allt är uppdaterat", "Alt er opdateret", "Alles aktuell",
        "Todo actualizado", "Tout est à jour", "Wszystko aktualne", "Усе актуально"),

    # about
    "About": ("Om", "Om", "Om", "Info", "Acerca de", "À propos", "O programie", "Про програму"),
    "About Whisper Runner": (
        "Om Whisper Runner", "Om Whisper Runner", "Om Whisper Runner", "Über Whisper Runner",
        "Acerca de Whisper Runner", "À propos de Whisper Runner", "O programie Whisper Runner",
        "Про Whisper Runner"),
    "Version {version}": (
        "Versjon {version}", "Version {version}", "Version {version}", "Version {version}",
        "Versión {version}", "Version {version}", "Wersja {version}", "Версія {version}"),
    "Whisper Runner transcribes audio and video files with OpenAI Whisper and shows the work as it "
    "happens: progress, time left, speed, and the transcript line by line. The transcript is saved as a "
    "text file next to the recording.\n\nEverything runs on this computer. Your recordings are never uploaded.": (
        "Whisper Runner transkriberer lyd- og videofiler med OpenAI Whisper og viser arbeidet mens det "
        "pågår: fremdrift, gjenværende tid, hastighet og transkripsjonen linje for linje. Transkripsjonen "
        "lagres som en tekstfil ved siden av opptaket.\n\nAlt kjøres på denne datamaskinen. Opptakene dine "
        "blir aldri lastet opp.",
        "Whisper Runner transkriberar ljud- och videofiler med OpenAI Whisper och visar arbetet medan det "
        "pågår: förlopp, återstående tid, hastighet och transkriptionen rad för rad. Transkriptionen sparas "
        "som en textfil bredvid inspelningen.\n\nAllt körs på den här datorn. Dina inspelningar laddas "
        "aldrig upp.",
        "Whisper Runner transskriberer lyd- og videofiler med OpenAI Whisper og viser arbejdet, mens det "
        "foregår: fremskridt, resterende tid, hastighed og transskriptionen linje for linje. "
        "Transskriptionen gemmes som en tekstfil ved siden af optagelsen.\n\nAlt kører på denne computer. "
        "Dine optagelser bliver aldrig uploadet.",
        "Whisper Runner transkribiert Audio- und Videodateien mit OpenAI Whisper und zeigt die Arbeit live: "
        "Fortschritt, verbleibende Zeit, Geschwindigkeit und das Transkript Zeile für Zeile. Das Transkript "
        "wird als Textdatei neben der Aufnahme gespeichert.\n\nAlles läuft auf diesem Computer. Ihre "
        "Aufnahmen werden nie hochgeladen.",
        "Whisper Runner transcribe archivos de audio y vídeo con OpenAI Whisper y muestra el trabajo mientras "
        "ocurre: progreso, tiempo restante, velocidad y la transcripción línea a línea. La transcripción se "
        "guarda como archivo de texto junto a la grabación.\n\nTodo se ejecuta en este equipo. Tus "
        "grabaciones nunca se suben.",
        "Whisper Runner transcrit des fichiers audio et vidéo avec OpenAI Whisper et montre le travail en "
        "direct : progression, temps restant, vitesse et transcription ligne par ligne. La transcription est "
        "enregistrée dans un fichier texte à côté de l'enregistrement.\n\nTout s'exécute sur cet ordinateur. "
        "Vos enregistrements ne sont jamais envoyés en ligne.",
        "Whisper Runner transkrybuje pliki audio i wideo za pomocą OpenAI Whisper i pokazuje pracę na "
        "bieżąco: postęp, pozostały czas, szybkość i transkrypcję wiersz po wierszu. Transkrypcja jest "
        "zapisywana jako plik tekstowy obok nagrania.\n\nWszystko działa na tym komputerze. Twoje nagrania "
        "nigdy nie są nigdzie wysyłane.",
        "Whisper Runner транскрибує аудіо- та відеофайли за допомогою OpenAI Whisper і показує роботу в "
        "реальному часі: прогрес, час, що залишився, швидкість і транскрипт рядок за рядком. Транскрипт "
        "зберігається як текстовий файл поруч із записом.\n\nУсе працює на цьому комп'ютері. Ваші записи "
        "ніколи нікуди не завантажуються."),
    "Checking for a newer version…": (
        "Ser etter en nyere versjon…", "Söker efter en nyare version…", "Søger efter en nyere version…",
        "Suche nach neuerer Version…", "Buscando una versión más reciente…",
        "Recherche d'une version plus récente…", "Szukanie nowszej wersji…", "Пошук новішої версії…"),
    "You have the latest version.": (
        "Du har den nyeste versjonen.", "Du har den senaste versionen.", "Du har den nyeste version.",
        "Sie haben die neueste Version.", "Tienes la última versión.", "Vous avez la dernière version.",
        "Masz najnowszą wersję.", "У вас найновіша версія."),
    "Version {version} is available. Get it from the project page below.": (
        "Versjon {version} er tilgjengelig. Last den ned fra prosjektsiden nedenfor.",
        "Version {version} finns. Hämta den från projektsidan nedan.",
        "Version {version} er tilgængelig. Hent den fra projektsiden nedenfor.",
        "Version {version} ist verfügbar. Sie erhalten sie auf der Projektseite unten.",
        "La versión {version} está disponible. Descárgala desde la página del proyecto, abajo.",
        "La version {version} est disponible. Téléchargez-la depuis la page du projet ci-dessous.",
        "Dostępna jest wersja {version}. Pobierz ją ze strony projektu poniżej.",
        "Доступна версія {version}. Завантажте її зі сторінки проєкту нижче."),
    "Couldn't check for a newer version. Are you online?": (
        "Kunne ikke se etter en nyere versjon. Er du koblet til internett?",
        "Kunde inte söka efter en nyare version. Är du ansluten till internet?",
        "Kunne ikke søge efter en nyere version. Er du online?",
        "Neuere Version konnte nicht gesucht werden. Sind Sie online?",
        "No se pudo buscar una versión más reciente. ¿Tienes conexión a internet?",
        "Impossible de rechercher une version plus récente. Êtes-vous connecté à Internet ?",
        "Nie udało się sprawdzić nowszej wersji. Czy masz połączenie z internetem?",
        "Не вдалося перевірити наявність новішої версії. Чи є підключення до інтернету?"),
    "Update available": (
        "Oppdatering tilgjengelig", "Uppdatering finns", "Opdatering tilgængelig", "Update verfügbar",
        "Actualización disponible", "Mise à jour disponible", "Dostępna aktualizacja", "Доступне оновлення"),
    "Skip this version": (
        "Hopp over denne versjonen", "Hoppa över den här versionen", "Spring denne version over",
        "Diese Version überspringen", "Omitir esta versión", "Ignorer cette version", "Pomiń tę wersję",
        "Пропустити цю версію"),
    "You won't be reminded about version {version}.": (
        "Du får ikke flere påminnelser om versjon {version}.",
        "Du påminns inte om version {version} igen.",
        "Du bliver ikke mindet om version {version} igen.",
        "Sie werden an Version {version} nicht mehr erinnert.",
        "No se te volverá a avisar de la versión {version}.",
        "Vous ne serez plus averti de la version {version}.",
        "Przypomnienia o wersji {version} zostały wyłączone.",
        "Нагадування про версію {version} вимкнено."),
    "Project page on GitHub": (
        "Prosjektside på GitHub", "Projektsida på GitHub", "Projektside på GitHub", "Projektseite auf GitHub",
        "Página del proyecto en GitHub", "Page du projet sur GitHub", "Strona projektu na GitHubie",
        "Сторінка проєкту на GitHub"),
    "MIT license": (
        "MIT-lisens", "MIT-licens", "MIT-licens", "MIT-Lizenz",
        "Licencia MIT", "Licence MIT", "Licencja MIT", "Ліцензія MIT"),
    "Close": ("Lukk", "Stäng", "Luk", "Schließen", "Cerrar", "Fermer", "Zamknij", "Закрити"),
}


TRANSLATIONS = {code: {en: texts[i] for en, texts in MESSAGES.items()} for i, code in enumerate(TRANSLATED)}
