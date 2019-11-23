### change_archive.py
This program takes a CSV file and replace the old archive urls (`webarchive.org.uk/wayback/archive/`) with new archive urls (`web.archive.org/web/`). The date will be replaced with the closest date.

Example: 

    old: 

    "UK archive","4","20090223153400","https://www.webarchive.org.uk/wayback/archive/20090223153400/http://www.adoptionuk.org/"

    new:  
    UK archive,4,20090221132018,https://web.archive.org/web/20090221132018/http://www.adoptionuk.org/

Command syntax: 
```
python3 change_archive.py <something>.csv
```

> The input csv must have the following header:
> archive_name, url_id, position, archive_url