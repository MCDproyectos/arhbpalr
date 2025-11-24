import zipfile
import pandas as pd
from datetime import datetime
import os
wd = os.getcwd()
print(wd)
progress_file = '.\progress_chunk.txt'
last_processed_chunk = -1
if os.path.exists(progress_file):
    with open(progress_file, 'r') as pf:
        last_processed_chunk = int(pf.read())
print("iniciando...",last_processed_chunk)
# Open the ZIP file
with zipfile.ZipFile(wd+'\\2024-eBird-dwca-1.0.zip') as z:
    # List all files inside the ZIP
    print(z.namelist())
    
    with z.open('eod_2024.csv') as f:
        s=100000
        
        # Read in chunks, filter rows before loading fully
        chunks = pd.read_csv(f, chunksize=s)
        
        i=0
        acum=0
        for i, chunk in enumerate(chunks):
            if i <= last_processed_chunk:
                # Skip already processed chunks
                print(i)
                continue
            try:
                #filtered = chunk[chunk['country'] == 'Mexico']
                filtered = chunk[chunk['stateprovince'] == 'Sonora']
                #filtered = chunk[chunk['county'] == 'Hermosillo']
                n = len(filtered.index)
                acum += n
                print(datetime.now(),i+1,n,acum)
                filtered.to_csv(wd+'\\filtered_output.csv', mode='a', header=not os.path.exists('filtered_output.csv'), index=False)
            except Exception as e:
                print(f"Error processing chunk {i}: {e}")
                # Optionally re-raise or handle error here if you want to stop
            
            finally:
                # Save progress regardless of success or failure
                with open(progress_file, 'w') as pf:
                    pf.write(str(i))
                    pf.flush()
                    os.fsync(pf.fileno())
