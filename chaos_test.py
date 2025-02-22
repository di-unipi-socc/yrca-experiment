import sys
import subprocess
import random
import time
from datetime import datetime

# Global vars
stack_name = ''
num_services = 0
tot_services = 0
cycles = 0
seconds = 0
dont_choose = ['onlineBoutique_logstash', 'onlineBoutique_frontend', 'onlineBoutique_loadgenerator', 'onlineBoutique_redis-cart']

# Help function
def help():
    print('\n┌─────────────────────── HOW TO USE ───────────────────────────┐')
    print('│                                                              │')
    print('│ python3 chaos_test.py STACK_NAME NUM_SERVICES CYCLES SECONDS │')
    print('│                                                              │')
    print('├───────────────────────── PARAMETERS ─────────────────────────┤')
    print('│                                                              │')
    print('│ STACK_NAME: onlineBoutique - Docker Swarm deploy name        │')
    print('│ NUM_SERVICES: 10 - Number of containers to stop              │')
    print('│ CYCLES: 3 - Repeat the chaos test for CYCLES times           │')
    print('│ SECONDS: 60 - Wait time between each cycle                   │')
    print('└──────────────────────────────────────────────────────────────┘\n')

# Check app parameters
def checkParams(args):
    global stack_name
    global tot_services
    global num_services
    global cycles
    global seconds

    stack_name = str(args[1])
    tot_services = int(subprocess.check_output('docker service ls | wc -l', shell=True)) - 1

    if (int(args[2]) <= 0 or int(args[2]) > tot_services):
        print('Invalid number of services, retry.\n')
        exit()
    num_services = int(args[2])

    if (int(args[3]) <= 0):
        print('Invalid cycles value, use positive integer higher than 1.\n')
        exit()
    cycles = int(args[3])

    if (int(args[4]) <= 0 and int(args[4]) > 600):
        print('Invalid seconds value, use positive integer values between 1 and 600.\n')
        exit()
    seconds = int(args[4])

    print('\n┌────────────────────────── CHAOS TEST ───────────────────────────')
    print('│')
    print('├── Stack:', stack_name)
    print('├── Total services: ' + str(tot_services) + ' (' + str(num_services) + ' removed)')
    print('├── Cycles:', cycles, '── Wait time:', seconds, 'sec')

# Applicaiton core logic
def run():
    # Open or create new logging file
    log_file = open('chaos_test.log', 'w')
    log_file.write('CHAOS TEST STARTED\n\n')

    random.seed(random.random())
    global cycles
    global seconds

    # Repeat choas test CYCLES times
    for cycle in range(cycles):
        removed_services = []
        print('│')
        print('├── Cycle #' + str(cycle + 1) + ' started')
        print('│ Removed services:')

        # Select two random services and remove containers
        while(len(removed_services) < num_services):
            position = random.randint(1, tot_services) + 1
            command = "docker service ls | head -" + str(position) + " | tail -1 | awk '{print $2}'"
            service_name = str(subprocess.check_output(command, shell=True))[2:-3]
            
            # Avoid removing logstash, loadgenerator and frontend containers
            if (service_name not in dont_choose and service_name not in removed_services):
                log_file.write(service_name + ' removed at ' + str(datetime.now())[:-3] + '\n')
                print('│ - ' + service_name + ' at ' + str(datetime.now())[:-3])
                subprocess.check_output('docker service scale ' + service_name + '=0', shell=True)
                removed_services.append(service_name)

        # Wait
        time.sleep(seconds)
        
        # Reactivate removed services
        for service in removed_services:
            subprocess.check_output('docker service scale ' + service + '=1', shell=True)
            container_insertion = False

            # Verify if the container has been added    
            while(not container_insertion):
                insertion_output = str(subprocess.check_output("docker service ls -f name=" + service + " | awk '{print $2}'", shell=True))

                if(insertion_output.find(service) != -1):
                    container_insertion = True
        
        time.sleep(60)
        
        # Log the container insertion
        for service in removed_services:
            log_file.write(service + ' added at ' + str(datetime.now())[:-3] + '\n')
        
        time.sleep(10)

    print('└──────────────────────────── FINISH ─────────────────────────────\n')
    log_file.write('\nCHAOS TEST ENDED\n')
    log_file.close()

# Main function
def main():
    if (len(sys.argv) != 5):
        help()
        exit()
    checkParams(sys.argv)
    run()

if __name__ == '__main__':
    main()
