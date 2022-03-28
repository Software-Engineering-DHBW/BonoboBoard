# Unittests

## Vorwort

Um etwaige Tests in diesem Verzeichnis nutzen zu können, müssen erst einmal die folgenden Pakete installiert werden:  
  
| Python Paket      | Version |
|:----------------- |:------- |
| selenium          | 4.1.3   |
| webdriver-manager | 3.5.4   |

Diese kann man ganz einfach über `pip3 install -U -r requirements.txt` installieren, wenn man im Verzeichnis [tests](https://github.com/Software-Engineering-DHBW/BonoboBoard/tree/main/bonobo-board/tests) ist.  
(Zum Verifizieren unter Ubuntu (Linux) einfach `pip3 list | grep -e selenium -e webdriver` eingeben)  

### Credentials

Die Umgebungsvariablen: **STUDENTMAIL**, **STUDENTPASS** und **STUDENTCOURSE** müssen gesetzt sein, damit etwaige Authentifizierungsprozesse funktionieren.  
Für **Windows** müssen die Umgebungsvariablen angepasst werden. Diese sind über das Startmenü -> Systemumgebungsvariablen bearbeiten -> Umgebungsvariablen -> Benutzervariablen zu erreichen. Mit Hilfe des Buttons "Neu" kann ein neuer Eintrag hinzugefügt werden. Der Name der Variablen entspricht dabei **STUDENTMAIL**, **STUDENTPASS** und **STUDENTCOURSE**, der Wert ist der zugehörige Wert.

### PYTHONPATH

Des Weiteren ist es nötig, das Verzeichnis [tests](https://github.com/Software-Engineering-DHBW/BonoboBoard/tree/main/bonobo-board/tests)
der Umgebungsvariable PYTHONPATH hinzuzufügen. Gewisse Imports beim Ausführen der Tests schlagen sonst fehl.  
  
Unter **Ubuntu/Linux** kann man das Ganze dauerhaft hinzufügen, in dem man in die Datei **.bashrc** unter dem Home-Verzeichnis des Benutzers (via `cd ~` zu erreichen)
folgende Zeilen an das Ende der Datei anhängt:  
```
bonobo_test_path="$HOME/path/to/bonobo-board/tests"
if [ "${PYTHONPATH##*${bonobo_test_path}}" == "$PYTHONPATH" ] && [ "${PYTHONPATH##*${bonobo_test_path}:*}" == "$PYTHONPATH" ]; then
    export PYTHONPATH="${PYTHONPATH:+${PYTHONPATH}:}${bonobo_test_path}"
fi
```

Unter **Windows** muss der PYTHONPATH in den Umgebungsvariablen angepasst werden. Fall mehr als ein Eintrag im PYTHONPATH besteht, sind diese durch ein Semikolon zu trennen. Der hinzuzufügende Pfad muss in etwa folgenden Ansprüchen C:\path\to\bonobo-board\tests genügen.

## Frontend UI

Im Verzeichnis [frontend_ui](https://github.com/Software-Engineering-DHBW/BonoboBoard/tree/main/bonobo-board/tests/frontend_ui) befindet sich die Datei 



[dhbw_test.py](https://github.com/Software-Engineering-DHBW/BonoboBoard/blob/main/bonobo-board/modules/dhbw_test.py)
[dhbw tests](https://github.com/Software-Engineering-DHBW/BonoboBoard/tree/main/bonobo-board/modules/dhbw/tests)
