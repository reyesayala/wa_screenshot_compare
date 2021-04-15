### change_archive.py
This program takes a CSV file and replace the old archive urls (`webarchive.org.uk/wayback/archive/`) with new archive urls (`web.archive.org/web/`). The date will be replaced with the closest date.

Example: 

    before: 

    "UK archive","4","20090223153400","https://www.webarchive.org.uk/wayback/archive/20090223153400/http://www.adoptionuk.org/"

    after:  
    UK archive,4,20090221132018,https://web.archive.org/web/20090221132018/http://www.adoptionuk.org/

Command syntax: 
```
python3 change_archive.py <something>.csv
```

> The input csv should have the following header:
>
> archive_name, url_id, position, archive_url

### rm_dup_with_sim.py
This program "cleans" a CSV file so that duplicating lines are removed. Only the url that has the latest date will be kept.

Example:

    before:

    http://www.runnymedetrust.org/","https://web.archive.org/web/20180224041155if_/https://www.runnymedetrust.org/","../pics_current//UKwebarchive.11.png","../pics_archive_combined//UK archive.11.20180224041155.png","0.62","30478.26","75.04"

    "http://www.runnymedetrust.org/","https://web.archive.org/web/20180831111101if_/https://www.runnymedetrust.org/","../pics_current//UKwebarchive.11.png","../pics_archive_combined//UK archive.11.20180831111101.png","0.79","11656.27","88.36"

    "http://www.runnymedetrust.org/","https://web.archive.org/web/20190406005849if_/https://www.runnymedetrust.org/","../pics_current//UKwebarchive.11.png","../pics_archive_combined//UK archive.11.20190406005849.png","0.80","12063.63","88.02"

    "http://www.runnymedetrust.org/","https://web.archive.org/web/20190622222140if_/https://www.runnymedetrust.org/","../pics_current//UKwebarchive.11.png","../pics_archive_combined//UK archive.11.20190622222140.png","0.79","20306.58","83.57"

    "http://www.runnymedetrust.org/","https://web.archive.org/web/20190914153402if_/https://www.runnymedetrust.org/","../pics_current//UKwebarchive.11.png","../pics_archive_combined//UK archive.11.20190914153402.png","0.97","801.09","99.20"

    after:

    "http://www.runnymedetrust.org/","https://web.archive.org/web/20190914153402if_/https://www.runnymedetrust.org/","../pics_current//UKwebarchive.11.png","../pics_archive_combined//UK archive.11.20190914153402.png","0.97","801.09","99.20"

Command syntax: 
```
python3 rm_dup_with_sim.py <something>.csv
```

### web_exist_csv.py
The program checks and records whether the url in the seed file is still available.

Example:

    Input:

    Seed URL,Group,Status,Frequency,Type,Access
    http://www.firstperspective.ca/news/2941-let-s-be-idle-no-more,,False,NONE,normal,True

    Output:

    "Id","url","availability","site_status","site_message"
    "1","http://www.firstperspective.ca/news/2941-let-s-be-idle-no-more","Website does not exist","FAIL","HTTPError: 403"


Command syntax: 
```
python3 web_exist_csv.py --input=Idle-No-More-seed-list.csv --output=out.csv --timeout=4
```
Arguments:
* input - The CSV file with the current urls.
* output - The CSV file to write the output.
* timeout - (optional) Specify duration before timeout, in seconds, default 30 seconds.
>
> "current_url", "archive_url", "current_file_name", "archive_file_name", "ssim_score", "mse_score", "vector_score"
