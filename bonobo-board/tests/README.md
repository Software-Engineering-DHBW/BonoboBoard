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

### PYTHONPATH

Des Weiteren kann es nötig sein, das Verzeichnis [tests](https://github.com/Software-Engineering-DHBW/BonoboBoard/tree/main/bonobo-board/tests)
der Umgebungsvariable PYTHONPATH hinzuzufügen, falls gewisse Imports beim Ausführen der Tests fehlschlagen sollten.  
  
Unter Ubuntu/Linux kann man das Ganze dauerhaft hinzufügen, in dem man in die Datei **.bashrc** unter dem Home-Verzeichnis des Benutzers (via `cd ~` zu erreichen)
folgende Zeilen an das Ende der Datei anhängt:  
```
bonobo_test_path="$HOME/path/to/bonobo-board/tests"
if [ "${PYTHONPATH##*${bonobo_test_path}}" == "$PYTHONPATH" ] && [ "${PYTHONPATH##*${bonobo_test_path}:*}" == "$PYTHONPATH" ]; then
    export PYTHONPATH="${PYTHONPATH:+${PYTHONPATH}:}${bonobo_test_path}"
fi
```

## Frontend UI

Im Verzeichnis [frontend_ui](https://github.com/Software-Engineering-DHBW/BonoboBoard/tree/main/bonobo-board/tests/frontend_ui) befindet sich die Datei 



[dhbw_test.py](https://github.com/Software-Engineering-DHBW/BonoboBoard/blob/main/bonobo-board/modules/dhbw_test.py)
[dhbw tests](https://github.com/Software-Engineering-DHBW/BonoboBoard/tree/main/bonobo-board/modules/dhbw/tests)
