# CipherAPI
This api works by interacting the database by API and not by mysql credentials.

sorry if im not detailed, if there's any issues about the api don't hesitate to 
submit an issue on github! :D

![ralsei](https://c.tenor.com/a67qt4MuklQAAAAM/ralsei-dancing-ralsei.gif)

# Table Of Contents
**Home**

- [Authentication](#authentication)

**GET API Endpoints**

- [/api/token_validate](#apitoken_validate)
- [/api/users](#apiusers)
- [/api/people](#apipeople)
- [/api/people/{id}](#apipeopleid)

**POST API Endpoints**

- [/api/people/add](#apipeopleadd)
- [/api/users/add](#apiusersadd)

# Authentication
In order to authenticate to the server, you'll have to create a
api token thru an administrator account, after that, authenticate 
thru ```x-api-key``` as the header then you insert your api token as the value.

Here's an example in python
```py
import os
import requests

key = 'CS_XXXXXXXXXXX'
BASE = "http://localhost:8080/api/people"

def main():
    headers = {
        "x-api-key": f"{key}",
        "User-Agent": "insomnia/11.6.1" # you can change this
    }
    r = requests.get(f"{BASE}", headers=headers)
    r.raise_for_status()
    
    print(r.json())

if __name__ == "__main__":
    main()
```

# /api/token_validate
```Method: GET```

This endpoint will validate if your token is valid or not.

# /api/users
```Method: GET```

Gets all users in the database.

# /api/people
```Method: GET```

As in the python example on the variable ```BASE``` on the authentication part, 
you'll be able to get everyone on the database.

# /api/people/{id}
```Method: GET```

You can pull specific people from the database instead of 
grabbing the entire database.

# /api/people/add
```Method: POST```

You can add people to the database by using this endpoint.

Example client JSON input:

```json
{
    "name": "John Doe",
    "address": "123 Main St, Anytown, USA",
    "phone": "555-123-4567",
    "email": "example@email.com",
    "ipaddress": "127.0.0.1",
    "label": "Dangerous", // this can be any other words by adding a comma like "armed, dangerous"
    "description": "This person is dangerous",
    "convicted": 1, // 1 = True, 0 = False 
    "socials": "https://twitter.com/johndoe"
}
```

> [!NOTE]
> "convicted" is a boolean value, so you can only use 1 or 0.
> If you were asking to yourself, ID is not editable as the MySQL table chooses the ID for you.
> ```sql
> id INT AUTO_INCREMENT PRIMARY KEY
> ```

# /api/users/add
```Method: POST (Administrator)```

Like people/add but its for users of cipherstorm

JSON Client input example:

```json
{
    "username": "ralsei",
    "password": "the-fun-gang!123"
}
```

> [!NOTE]
> Passwords are hashed using bcrypt, so you don't need to worry about that.
