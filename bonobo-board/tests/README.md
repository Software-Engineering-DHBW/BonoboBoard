# Unittests

## Vorwort

To be able to use any tests in this directory, the following packages must first be installed:
  
| Python Paket      | Version |
|:----------------- |:------- |
| selenium          | 4.1.3   |
| webdriver-manager | 3.5.4   |

These can be easily installed via `pip3 install -U -r requirements.txt` if you are in the [tests](https://github.com/Software-Engineering-DHBW/BonoboBoard/tree/main/bonobo-board/tests) directory.
(To verify under Ubuntu (Linux) just type `pip3 list | grep -e selenium -e webdriver`)

### Credentials

The environment variables: **STUDENTMAIL**, **STUDENTPASS** and **STUDENTCOURSE** must be set for any authentication processes to work.  
For **Windows**, the environment variables must be adjusted. These can be accessed via the Start menu -> Edit System Environment Variables -> Environment Variables -> User Variables. A new entry can be added using the "New" button. The name of the variable corresponds to **STUDENTMAIL**, **STUDENTPASS** or **STUDENTCOURSE**, the value is the corresponding value.

### PYTHONPATH

Furthermore, it is necessary to add the directory [tests](https://github.com/Software-Engineering-DHBW/BonoboBoard/tree/main/bonobo-board/tests) to the environment variable PYTHONPATH. Certain imports when running the tests will otherwise fail.

Under **Ubuntu/Linux** you can add it permanently by adding the following lines to the end of the **.bashrc** file under the user's home directory (reachable via `cd ~`):
```
bonobo_test_path="$HOME/path/to/bonobo-board/tests"
if [ "${PYTHONPATH##*${bonobo_test_path}}" == "$PYTHONPATH" ] && [ "${PYTHONPATH##*${bonobo_test_path}:*}" == "$PYTHONPATH" ]; then
    export PYTHONPATH="${PYTHONPATH:+${PYTHONPATH}:}${bonobo_test_path}"
fi
```

Under Windows, the PYTHONPATH must be adjusted in the environment variables. If there is more than one entry in the PYTHONPATH, separate them with a semicolon. The path to be added must approximately meet the following requirements C:\path\to\bonobo-board\tests.

## Frontend UI

The directory [frontend_ui](https://github.com/Software-Engineering-DHBW/BonoboBoard/tree/main/bonobo-board/tests/frontend_ui) contains the file



[dhbw_test.py](https://github.com/Software-Engineering-DHBW/BonoboBoard/blob/main/bonobo-board/modules/dhbw_test.py)
[dhbw tests](https://github.com/Software-Engineering-DHBW/BonoboBoard/tree/main/bonobo-board/modules/dhbw/tests)
