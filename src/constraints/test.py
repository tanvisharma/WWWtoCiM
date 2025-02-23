import subprocess
import csv

def main():
    with open('../my-inputs/workloads/workloads.txt', 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)  # Skip the header row

        for row in reader:
            M = row[1]
            N = row[2]
            K = row[3]

            # Run main.py with the M, N, and K values as command line arguments
            subprocess.run(['python', 'main.py', '--M', M, '--N', N, '--K', K, '--Smem', '256'])

if __name__ == "__main__":
    main()
