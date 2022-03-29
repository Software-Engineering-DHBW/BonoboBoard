# Unittests

## Requirements

To be able to use any tests in this directory, the following packages must first be installed:
  
| Python Paket      | Version |
|:----------------- |:------- |
| selenium          | 4.1.3   |
| webdriver-manager | 3.5.4   |

These can be easily installed via `pip3 install -U -r requirements.txt` if you are in the [tests](https://github.com/Software-Engineering-DHBW/BonoboBoard/tree/main/bonobo-board/tests) directory.
(To verify under Ubuntu/Linux just type `pip3 list | grep -e selenium -e webdriver`)

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

## Setup Changes

If the local setup uses a different port or uses SSL encryption, the [frontend_config.py](https://github.com/Software-Engineering-DHBW/BonoboBoard/blob/main/bonobo-board/tests/frontend_config.py) file must be modified. To do this, simply enter the port used in the **PORT** variable and replace the _http_ with _https_ in **PROTOCOL**.

## Frontend UI

The directory [frontend_ui](https://github.com/Software-Engineering-DHBW/BonoboBoard/tree/main/bonobo-board/tests/frontend_ui) contains the file
[pages_ui.py](https://github.com/Software-Engineering-DHBW/BonoboBoard/tree/main/bonobo-board/tests/frontend_ui/pages_ui.py) which can be used to run tests on the frontend. The UI of the frontend is tested in Chrome, Firefox and Brave using selenium.
To test the functionality just run `python3 pages_ui.py` inside the _frontend_ui_ directory.

## Feature Test: Leistungsübersicht

In the [tests](https://github.com/Software-Engineering-DHBW/BonoboBoard/tree/main/bonobo-board/tests) directory there are also tests that test complete features of the BonoboBoard product. So far, there is an assembled feature test, called [leistungsuebersicht.py](https://github.com/Software-Engineering-DHBW/BonoboBoard/blob/main/bonobo-board/tests/leistungsuebersicht.py), for the "Leistungsübersicht".  
It tests in the frontend all the required steps until you can see your notes and also checks if they show the appropriate content.  
In the backend it tests the functionality of the [dualis](https://github.com/Software-Engineering-DHBW/BonoboBoard/blob/main/bonobo-board/modules/dhbw/dualis.py) module, which is used for scraping the notes.

To run this feature test simply type `python3 leistungsuebersicht.py` inside your terminal (remember to change directories to _tests_ before trying to execute the mentioned command).  
You can choose for which browser you want to test this feature by using the `-b` or `--browser` option.  
Currently Chrome, Brave and Firefox are supported, but the selected browsers must be installed locally.  
The command to perform this test for Chrome and Brave looks like this: `python3 leistungsuebersicht.py -b chrome brave`.  
(Check `python3 leistungsuebersicht --help` for more help!)  
  
A successful run of the test for Firefox looks like this:
```
test_login (dhbw.tests.dualis_test.TestDualisImporter)
Test dualis login functionality. ... ok
test_scrape (dhbw.tests.dualis_test.TestDualisImporter)
Test scraping functionality. ... ok
test_logout (dhbw.tests.dualis_test.TestDualisImporter)
Test logout functionality. ... ok
test_leistungsuebersicht (frontend_ui.pages_ui.TestPagesUI)
test every feature of leistungsuebersicht ... 

====== WebDriver manager ======
Current firefox version is 98.0
Get LATEST geckodriver version for 98.0 firefox
Driver [/home/jakob/.wdm/drivers/geckodriver/linux64/v0.30.0/geckodriver] found in cache
ok

----------------------------------------------------------------------
Ran 4 tests in 18.806s

OK
```

## Backend

To run the backend tests or use the individual importers for your own purposes, it is again necessary to extend the PYTHONPATH environment variable with the path to the directory /path/to/bonobo-board/modules. A guide to realize this is already defined in the [this](https://github.com/Software-Engineering-DHBW/BonoboBoard/blob/main/bonobo-board/tests/README.md#pythonpath) section.
  
The unit tests for the backend can be found in the [tests](https://github.com/Software-Engineering-DHBW/BonoboBoard/tree/main/bonobo-board/modules/dhbw/tests) directory under _bonobo-board/modules/dhbw_.
The execution of the unit tests can be controlled via the script [dhbw_test.py](https://github.com/Software-Engineering-DHBW/BonoboBoard/blob/main/bonobo-board/modules/dhbw_test.py). This script can run all tests defined in the directory or only a subset of tests with the `-t` flag.
For more details execute the command `python3 dhbw_test.py --help`.  
  
For example, a successful execution of `python3 dhbw_test.py -t zimbra` looks like that:
```
test_login (dhbw.tests.zimbra_test.TestZimbraHandler)
Test login functionality. ... ok
test_scrape (dhbw.tests.zimbra_test.TestZimbraHandler)
Test scraping functionality. ... ok
test_get_contacts (dhbw.tests.zimbra_test.TestZimbraHandler)
Test get contacts functionality. ... ok
test_new_contact (dhbw.tests.zimbra_test.TestZimbraHandler)
Test creating a new contact. ... 

>>> Created Contact: "True"

ok
test_remove_contact (dhbw.tests.zimbra_test.TestZimbraHandler)
Test removing an existing contact (created by test_new_contact). ... 

>>> Removing contact with firstName "unittest" and id "9680"
>>> Contact found locally: "False"

ok
test_send_mail (dhbw.tests.zimbra_test.TestZimbraHandler)
Test send mail functionality by sending a mail. ... ok
test_logout (dhbw.tests.zimbra_test.TestZimbraHandler)
Test logout functionality. ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.932s

OK
```
