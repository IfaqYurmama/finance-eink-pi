# finance-raspi

Fork von oberhamsi's finance-eink-raspi Projekt mit leichten Erweiterungen, Stabilisierungs-Fixes und noch mehr Spaghetti-Code

Für weitere Infos das Original-Repo abchecken: https://github.com/oberhamsi/finance-eink-pi 

Im Gegensatz zum Original unterstützt diese Version zwei abwechselnde Seiten mit Tickern. Da die Liste alphabetisch sortiert ist, habe ich mir einen DAX- und einen NASDAQ-ETF rausgesucht, die beide eine geringe Tracking-Differenz aufweisen um sie als Indikator für den Gesamtmarkt nutzen zu können. 

Die ISIN muss immer auf tradegate.de zu finden sein und die symbols.py muss im vorgegebenen Format gehalten werden, da es sonst zu Problemen kommt.

Um die Ticker-Seiten zu switchen habe ich mich zweier Cronjobs bedient die abwechselnd und jeweils um 5 Minuten versetzt ausgeführt werden:

    5,15,25,35,45,55 * * * 1-5 /usr/bin/python3 /home/pi/finance-eink-pi/main.py 1
    0,10,20,30,40,50 * * * 1-5 /usr/bin/python3 /home/pi/finance-eink-pi/main.py 2
    
Die `1` und die `2` sind dabei die Indikation, welche Seite geladen werden soll. Spaghetti-Code-Warnung: Es werden nur genau zwei Seiten unterstützt, für größere Flexibilität müsste der Code umgebaut werden.
