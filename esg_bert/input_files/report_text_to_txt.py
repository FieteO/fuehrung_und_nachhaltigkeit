import os
import pandas as pd
reports = pd.read_csv('../../reports.csv')

for index, row in reports.iterrows():
    filename = os.path.basename(row.filepath)
    with open(filename[:-4] + '.txt', 'w') as file:
        file.write(row.text)