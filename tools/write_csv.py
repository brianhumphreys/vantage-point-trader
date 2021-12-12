
import csv
import os

def writeResultsToCSV(filename: str, strat: str, params: str, result: int):
    writepath = '../results/results-{}.csv'.format(filename)
    mode = 'a' if os.path.exists(writepath) else 'w'
    with open(writepath, mode, newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')

        print(result)
        writer.writerow([strat, params, result])

    

