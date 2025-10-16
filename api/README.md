# CipherAPI
This api works by interacting the database by API and not by mysql credentials.

sorry if im not detailed.

![ralsei](https://c.tenor.com/a67qt4MuklQAAAAM/ralsei-dancing-ralsei.gif)

# Authentication
In order to authenticate to the server, you'll have to create a
api token thru an administrator account, after that, authenticate 
thru ```x-api-key``` as the header then you api token as the value.

Here's an example in python
```py
import os
import requests

key = 'CS_XXXXXXXXXXX'
BASE = "http://localhost:8080/api/people"

def main():
    headers = {
        "x-api-key": f"{key}",
        "User-Agent": "insomnia/11.6.1"
    }
    r = requests.get(f"{BASE}", headers=headers)
    r.raise_for_status()
    
    print(r.json())

if __name__ == "__main__":
    main()
```

Obviously you can change the ```User-Agent``` but yea 