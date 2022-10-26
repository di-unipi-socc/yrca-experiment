# yRCA Experiments
The following repository is used to document all the performed scenario analyzed in Luca Roveroni's Master Thesis project.

##  Online Boutique
All the available material refers to Online Boutique application that have been modified to be [log-enabled](https://github.com/di-unipi-socc/log-enabled-online-boutique).
To simplify the deployment process a docker-compose.yml file has been developed to run Online Boutique with Docker Swarm and a logstash.conf file to correctly parse and transform the incoming logs from Docker.
Use the personalized scripts inside the /scripts folder to run and stop the application, furthermore execute yRCA tests accordingly the proposed scanarios.

The results obtain by the master thesis project are structured as the following structure:
- Scenario X
  - all.json (log file generated by Online Boutique)
  - /src (contains all the source code files that have been modified to run tests)
  - yrca_output.png (yRCA output screenshot)
  - readme.txt (brief scenario explaination with command to execute)

## Run tests
Every scenario can be tested by simply replacing the files inside the "src" folder into the corresponding Online Boutique's microservice folder.

Follow the readme.txt file in each "Scenario" folder to run the desired test.

## Help
For any doubts or support, feel free to contact me via email at luca.roveroni@studenti.unipi.it
