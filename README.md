# BonoboBoard

| **Projektname**   | <img src="https://github.com/Software-Engineering-DHBW/BonoboBoard/blob/main/documents/latex_template/img/BonboBoardLogoWhite.png" height="64">|
| :---------------- | :----------- |
| **Unsere Vision** | BonoboBoard wird ein kostenfreier webbasierter Service für alle Studierenden der DHBW Mannheim, die statt vieler unabhängiger Websites eine einzige Übersicht aller auf die Hochschule bezogenen Inhalte erhalten wollen. Es soll Funktionen bereit stellen, die alle relevanten Websites der DHBW Mannheim nach Informationen durchsuchen und diese in Form eines Dashboards darstellen. |

## The Prototype

To ensure that our project is possible, we created a prototype for two of your core-features.    
This is how you get them to run:

**************************** 

### Requirements
- [Anaconda](https://www.anaconda.com/products/individual) to run python scripts
- Python-Packages
  - ``` BeautifulSoup ```
  - ``` pandas ```
  - ``` icalendar```
  - ``` requests ```
  - ``` re ```
  - ``` sys ```
- check them by opening a python-shell and type ``` import *package* ```
  - if this throws no errors, you have already fulfilled the package requirement

****************************  

### Dualis-Importer
1. Navigate into the folder 
   - ```BonoboBoard/django-datta-able-1.0.4/apps/dhbw/``` 
2. Start the Dualis-Crawler
   - Open a [**Anaconda**](https://www.anaconda.com/products/individual) shell in the specified folder
   - be sure to fulfill the above specified package requirements!
   - Commands in the anaconda-shell:
     - ```python```
     - ```from dualis_importer import DualisImporter```
     - ```DualisImporter(studentMail, password)```
       - where studentMail contains your student-mail as a string
       - where password contains your DHBW-password
<br>

<details> <summary>In case you don't have DHBW-Credentials, <b>expand this</b> for the results:</summary>
    
``` json
{
   "2":{
      "modul":"T3INF1001",
      "subject":"Mathematik I",
      "grade":"18",
      "credits":"80",
      "status":"nan",
      "date":"nan"
   },
   "3":{
      "modul":"T3INF1002",
      "subject":"Theoretische Informatik I",
      "grade":"20",
      "credits":"50",
      "status":"nan",
      "date":"nan"
   },
   "4":{
      "modul":"T3INF1003",
      "subject":"Theoretische Informatik II",
      "grade":"15",
      "credits":"50",
      "status":"nan",
      "date":"nan"
   },
   "5":{
      "modul":"T3INF1004",
      "subject":"Programmieren",
      "grade":"10",
      "credits":"90",
      "status":"nan",
      "date":"nan"
   },
   "6":{
      "modul":"T3INF1005",
      "subject":"SchlÃ¼sselqualifikationen",
      "grade":"15",
      "credits":"50",
      "status":"nan",
      "date":"nan"
   },
   "7":{
      "modul":"T3INF1006",
      "subject":"Technische Informatik I",
      "grade":"16",
      "credits":"50",
      "status":"nan",
      "date":"nan"
   },
   "8":{
      "modul":"T3INF2001",
      "subject":"Mathematik II",
      "grade":"15",
      "credits":"60",
      "status":"nan",
      "date":"nan"
   },
   "9":{
      "modul":"T3INF2002",
      "subject":"Theoretische Informatik III",
      "grade":"14",
      "credits":"60",
      "status":"nan",
      "date":"nan"
   },
   "10":{
      "modul":"T3INF2003",
      "subject":"Software Engineering I",
      "grade":"10",
      "credits":"90",
      "status":"nan",
      "date":"nan"
   },
   "11":{
      "modul":"T3INF2004",
      "subject":"Datenbanken",
      "grade":"11",
      "credits":"60",
      "status":"nan",
      "date":"nan"
   },
   "12":{
      "modul":"T3INF2005",
      "subject":"Technische Informatik II",
      "grade":"15",
      "credits":"80",
      "status":"nan",
      "date":"nan"
   },
   "13":{
      "modul":"T3INF2006",
      "subject":"Kommunikations- und Netztechnik",
      "grade":"10",
      "credits":"50",
      "status":"nan",
      "date":"nan"
   },
   "14":{
      "modul":"T3INF3001",
      "subject":"Software Engineering II",
      "grade":"nan",
      "credits":"nan",
      "status":"nan",
      "date":"nan"
   },
   "15":{
      "modul":"T3INF3002",
      "subject":"IT-Sicherheit",
      "grade":"16",
      "credits":"50",
      "status":"nan",
      "date":"nan"
   },
   "16":{
      "modul":"T3_3101",
      "subject":"Studienarbeit",
      "grade":"nan",
      "credits":"nan",
      "status":"nan",
      "date":"nan"
   },
   "17":{
      "modul":"T3_1000",
      "subject":"Praxisprojekt I",
      "grade":"b",
      "credits":"200",
      "status":"nan",
      "date":"nan"
   },
   "18":{
      "modul":"T3_2000",
      "subject":"Praxisprojekt II",
      "grade":"25",
      "credits":"200",
      "status":"nan",
      "date":"nan"
   },
   "19":{
      "modul":"T3_3000",
      "subject":"Praxisprojekt III",
      "grade":"nan",
      "credits":"nan",
      "status":"nan",
      "date":"nan"
   },
   "21":{
      "modul":"T3INF4104",
      "subject":"Elektrotechnik",
      "grade":"16",
      "credits":"30",
      "status":"nan",
      "date":"nan"
   },
   "22":{
      "modul":"T3INF4105",
      "subject":"Physik",
      "grade":"14",
      "credits":"50",
      "status":"nan",
      "date":"nan"
   },
   "23":{
      "modul":"T3INF4302",
      "subject":"Systemarchitekturen der Informationstechnik",
      "grade":"nan",
      "credits":"nan",
      "status":"nan",
      "date":"nan"
   },
   "24":{
      "modul":"T3INF4303",
      "subject":"Computergraphik und Bildverarbeitung",
      "grade":"nan",
      "credits":"nan",
      "status":"nan",
      "date":"nan"
   },
   "25":{
      "modul":"T3INF4111",
      "subject":"Grundlagen der Hard- und Software (MA-TINF19IT2)",
      "grade":"13",
      "credits":"50",
      "status":"nan",
      "date":"nan"
   },
   "26":{
      "modul":"T3INF4252",
      "subject":"Messdatenerfassung und -verarbeitung",
      "grade":"15",
      "credits":"50",
      "status":"nan",
      "date":"nan"
   },
   "27":{
      "modul":"T3INF4275",
      "subject":"Business Process Management",
      "grade":"15",
      "credits":"50",
      "status":"nan",
      "date":"nan"
   },
   "28":{
      "modul":"T3INF4331",
      "subject":"Maschinelles Lernen",
      "grade":"18",
      "credits":"50",
      "status":"nan",
      "date":"nan"
   },
   "29":{
      "modul":"T3INF4367",
      "subject":"EinfÃ¼hrung in die Robotik",
      "grade":"22",
      "credits":"50",
      "status":"nan",
      "date":"nan"
   },
   "33":{
      "modul":"T3_3300",
      "subject":"Bachelorarbeit",
      "grade":"nan",
      "credits":"nan",
      "status":"nan",
      "date":"nan"
   },
   "GPA":{
      "total_gpa_grade":"1,6",
      "major_subject_gpa_grade":"1,6"
   }
}

```
</details>    
As you can see, it is possible to get all DHBW related grades with a python script.    

****************************    

### Lecture-Importer

1. Navigate into the folder 
   - ```BonoboBoard/django-datta-able-1.0.4/apps/dhbw/``` 
2. Start the Crawler to retrieve all courses
   - Open a [**Anaconda**](https://www.anaconda.com/products/individual) shell in the specified folder
   - be sure to fulfill the above specified package requirements!
   - Commands in the anaconda-shell:
     - ```python```
     - ```from dualis_importer import CourseImporter```
     - ```course_importer = CourseImporter()```
     - ```course_importer.course_list```
   - Now you see an array of all courses:
``` 
['WIB18 A', 'WIB18 B', 'WIB18 BI', 'WSTL18 A', ... , 'TIE20 EN', 'TIE20 SE', 'TIE21 EN', 'TIE21 SE']
```

3. Start the Crawler to retrieve the lectures for a specified course
   - Open a [**Anaconda**](https://www.anaconda.com/products/individual) shell in the specified folder
   - be sure to fulfill the above specified package requirements!
   - Commands in the anaconda-shell:
     - ```python```
     - ```from dualis_importer import LectureImporter```
     - ```lecture_importer = LectureImporter(7761001)```
       - where 7761001 is the uid for the course "TINF19-IT2"
     - ```course_importer.course_list```
   - Now you see a pandas.DataFrame of all lectures:
``` 
                            lecture location               start                 end
0                        Statistik           2021-04-06 09:00:00 2021-04-06 11:30:00
1    Einführung in Matlab/Simulink           2021-04-06 13:00:00 2021-04-06 16:30:00
2                        Statistik           2021-04-13 09:00:00 2021-04-13 11:30:00
3    Einführung in Matlab/Simulink           2021-04-13 13:00:00 2021-04-13 16:30:00
4                        Statistik           2021-04-20 09:00:00 2021-04-20 11:30:00
..                              ...      ...                 ...                 ...
414             Blockchain (online)          2022-02-26 09:00:00 2022-02-26 12:15:00
415             Blockchain (online)          2022-02-26 13:00:00 2022-02-26 14:30:00
416             Blockchain (online)          2022-02-19 09:00:00 2022-02-19 12:15:00
417             Blockchain (online)          2022-02-19 13:00:00 2022-02-19 14:30:00
418   Klausur: Wahlmodul Informatik          2022-04-08 09:00:00 2022-04-08 11:00:00
``` 

So it is proven, that we can get information about all courses and their lectures. Isn't that great?

