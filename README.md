# BonoboBoard

| **Projektname** | <img src="https://github.com/Software-Engineering-DHBW/BonoboBoard/blob/main/documents/img/BonboBoardLogoWhite.png" height="64" > |
| ---------------| ----------------------- |
|**Unsere Vision** | BonoboBoard wird ein kostenfreier webbasierter Service für alle Studierenden der DHBW Mannheim, die statt vieler unabhängiger Websites eine einzige Übersicht aller auf die Hochschule bezogenen Inhalte erhalten wollen. Es soll Funktionen bereit stellen, die alle relevanten Websites der DHBW Mannheim nach Informationen durchsuchen und diese in Form eines Dashboards darstellen.|
|**Teammitglieder** | patpatwithhat, Na1k, J4ywng, Av3g3n, Firomaeor |

## User Manual
The user manual is located in [documents/product_documentation](https://github.com/Software-Engineering-DHBW/BonoboBoard/blob/main/documents/product_documentation/product_documentation.pdf).  
Please be aware, that we only use your credentials to log in to your DHBW-Mannheim accounts (Zimbra, Moodle, Dualis). This project is non-profit, **we do not forward your personal data to anyone**.  
Because this project is open source, it's fully transparent how we process your data.

## GitHub team-codex

1)  <font size="+20">Don't change the main branch directly.</font> Only update the main by merge requests. <br> 
Exceptions are made for new documents or their content.

2) Branches shall be named after the following convention: **\<category>/\<purpose>** <br>
examples for categories:  
	 * core  
	 * frontend  
	 * feature  
	 * bugfix  
	 * test  
examples: "feature/mobile_navbar" or "test/session_handling"<br>

3) **Merge Requests**: <br>
	Need **approvals of two** team members.<br>
	The person requesting has to merge him- or herself.<br>

## GitHub Actions
We use multiple GitHub Actions to automate our workflow. All workflows are located in [/BonoboBoard/.github/workflows/](https://github.com/Software-Engineering-DHBW/BonoboBoard/tree/main/.github/workflows). If you desire to make changes to these workflow files, mention it in your pull-request.  
Some actions use secrets. Thats why a team-member of Optima-Connect may has to approve workflow runs. Every attempt to steal secrets from this repository will result in further actions.  
All workflows run in different environments. You can see the status of the last deployment on the overview-site of this repository in GitHub. 

### Auto-Docs workflow
Builds the documentation on every push on main using [sphinx](https://www.sphinx-doc.org/en/master/). No approvals of team-members are required for deployment.   
The documentation is deployed on the [GitHub page](https://software-engineering-dhbw.github.io/BonoboBoard/) for this repo.

### env-unittests workflow
Runs the tests specified in [dhbw_test.py](https://raw.githubusercontent.com/Software-Engineering-DHBW/BonoboBoard/main/bonobo-board/modules/dhbw_test.py). This action gets called on every opened pull-request.

### test_and_deploy workflow
Runs unittests first, then deploys the main branch on the productive server.


## Local/Developer Setup
If you desire to run BonoboBoard on your local machine, please follow the instructions mentioned in documents/product_documentation.  
If you want to contribute to this project, please be sure to check out our [documentation-folder](https://github.com/Software-Engineering-DHBW/BonoboBoard/tree/main/documents) and GitHub-pages first. This provides you with the knowledge how we set up this project and which style-guidelines are applied.  
Short summary of the setup-process:
1) Install docker and docker-compose
2) Clone the repository
3) Build the images using the [```build_image``` script](https://github.com/Software-Engineering-DHBW/BonoboBoard/blob/main/bonobo-board/build_image)
4) Run ```docker-compose up```
5) Type http://localhost:80/ in a webbrowser

## More information/documentation
For more information/documentation about this project please have a look at our [documents-folder](https://github.com/Software-Engineering-DHBW/BonoboBoard/tree/main/documents) or this [README](https://github.com/Software-Engineering-DHBW/BonoboBoard/blob/main/bonobo-board/tests/README.md) for unit tests.  
For example you can find our style guides, used tools or third-party libraries there.  
Feel free to contact the developer-team, if you have questions or need further information.
