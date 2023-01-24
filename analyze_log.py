import subprocess
import json
from dateutil import parser

# Global vars
total_errors = 0
no_found_errors = 0
errors_correct_rootcause = 0
root_causes_found = 0
correct_root_causes = 0
explanations = []
removed_services = {}
services = ['adservice', 'cartservice', 'checkoutservice', 'currencyservice', 'emailservice', 'paymentservice', 'productcatalogservice', 'recommendationservice', 'shippingservice', 'redis-cart']

folder_path = 'tests/chaos/test1/'

# Parse log file and extract error logs only
def prepare():
    global removed_services
    
    # Copy all necessary files
    subprocess.check_output('cp ' + folder_path + 'chaos_test.log .', shell=True)
    subprocess.check_output('cp ' + folder_path + 'all.json .', shell=True)
    subprocess.check_output('cat all.json | grep ERROR > all_errors.json', shell=True)
    
    # Open chaos_script.log file
    chaos_log = open('chaos_test.log', 'r')
    lines = chaos_log.readlines()[2:-2]
    
    # Convert file lines in hashmap for better look up
    for line in lines:
        values = line.split(' ')
        timestamp = str(values[3]) + 'T' + str(values[4][:-2]) + 'Z'
        service_name = values[0]

        if service_name not in removed_services:
            removed_services[service_name] = []

        # Insert timestamps: first remotion timestamp and second insertion timestamp
        removed_services[service_name].append(timestamp)
    
    print(removed_services)

# Open log file and analyze it
def analyze():
    global total_errors
    global explanations
    global root_causes_found
    global errors_correct_rootcause
    global no_found_errors
    global services
    
    # Read errors
    log_file = open('all_errors.json', 'r')
    lines = log_file.readlines()
    total_errors = len(lines)
    
    # Iterate over errors and execute yRCA
    for line in lines:
        error_file = open('error.json', 'w')
        error_file.write(line)
        error_file.close()

        # Get error timestamp for further checks
        with open('error.json') as json_file:
            data = json.load(json_file)
        timestamp = str(data['message'].split(' - ')[0])

        # Execute yRCA and let it explain the error
        yrca_output = str(subprocess.check_output('./scripts/yrca.sh', shell=True))[2:-3]

        # Looking for root cause and compare it with chaos_test.log
        # We can distinguish three possible yrca outputs:
        # 1. Found no failure
        # 2. Cascade failure(s) with one root cause
        # 3. Cascade failure(s) with more than one root causes
        if (yrca_output.find('Found no failure') == -1):
            
            # Looking for number of explanations
            position = yrca_output.find('possible explanation') - 2
            explanations.append(int(str(yrca_output[position])))
            
            # Case 1. else Case 2.
            if (yrca_output[0:2] == '[1'):
                root_causes_found += 1
                root_cause_service = str(yrca_output.split(':')[-2].split('>')[-1].strip())
                cause = False

                if (root_cause_service in services):
                    cause = searchContainer('onlineBoutique_' + root_cause_service, timestamp)
                else:
                    root_cause_service = str(yrca_output.split(':')[1].strip())
                    cause = searchContainer('onlineBoutique_' + root_cause_service, timestamp)
                
                # Count if the error has a scorrect root cause
                if (cause):
                    errors_correct_rootcause += 1
                else:
                    print('yRCA output:')
                    print(yrca_output)
                    print('\nAssociated error:')
                    print(line + '\n')
            else:
                found_explanations = yrca_output.split('[0.')
                found_explanations.pop(0)
                causes = []
                
                for explanation in found_explanations:
                    root_causes_found += 1
                    root_cause_service = str(yrca_output.split(':')[-2].split('>')[-1].strip())

                    if (root_cause_service in services):
                        causes.append(searchContainer('onlineBoutique_' + root_cause_service, timestamp))
                    else:
                        root_cause_service = str(yrca_output.split(':')[1].strip())
                        causes.append(searchContainer('onlineBoutique_' + root_cause_service, timestamp))
                
                # Count if the error has all corrected root causes
                if all(cause is True for cause in causes):
                    errors_correct_rootcause += 1
                else:
                    print('yRCA output:')
                    print(yrca_output)
                    print('\nAssociated error:')
                    print(line + '\n')
        else:
            no_found_errors += 1
            print('yRCA output:')
            print(yrca_output)
            print('\nAssociated error:')
            print(line + '\n')

# Search inside chaos_test.log file if serviceName has been removed
# in that period. If found, +1 on correct_root_causes
def searchContainer(serviceName, timestamp):
    global correct_root_causes
    global removed_services
    
    # Parse timestramp from string to date type
    error = parser.parse(timestamp)
    correct_cause = False

    # Get timestamps for service down period if service exists
    if serviceName not in removed_services:
        return correct_cause
    
    remotion_period = removed_services[serviceName]

    # Compare error timestamp with down time period
    for i in range(0, len(remotion_period), 2):
        start = parser.parse(remotion_period[i])
        end = parser.parse(remotion_period[i + 1])
        
        if (start <= error <= end):
            correct_root_causes += 1
            correct_cause = True
    
    return correct_cause

def visualize():
    global explanations
    global total_errors
    global root_causes_found
    global errors_correct_rootcause
    global correct_root_causes
    global no_found_errors

    output = open('analyze.out', 'w')

    # Precision formulas
    avg_explanations = sum(explanations) / total_errors
    precision1 = correct_root_causes / root_causes_found
    precision2 = errors_correct_rootcause / total_errors
    
    # Build final statistics and save them
    output_line = 'Total number of explanations: ' + str(sum(explanations)) + '\n'
    output_line += 'Total number of errors: ' + str(total_errors) + '\n'
    output_line += 'Errors without explanation: ' + str(no_found_errors) + '\n'
    output_line += 'Total number of root causes: ' + str(root_causes_found) + '\n'
    output_line += 'Errors with correct root causes: ' + str(errors_correct_rootcause) + '\n'
    output_line += 'Correct root causes: ' + str(correct_root_causes) + '\n'
    output_line += 'Average number of explanations per error: ' + str(round(avg_explanations, 2)) + '\n'
    output_line += 'yRCA Precision 1 (correct root causes / root causes found): ' + str(round(precision1, 2) * 100) + '%\n'
    output_line += 'yRCA precision 2 (errors with correct root causes / total errors): ' + str(round(precision2, 2) * 100) + '%\n'

    output.write(output_line)
    output.close()

# Main function
def main():
    prepare()
    analyze()
    visualize()

if __name__ == '__main__':
    main()