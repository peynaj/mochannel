User & Channel blog REST app with follow, like, bookmark, file uploading 
by DRF (Django REST Framework) 
in relational database (sqlite or postgresql)
and authentication by JWT


### Requirements
- python3
- virtualenv
- sqlite or postgresql


### Instalation

```shell
$ git clone GIT_REPO
$ cd GIT_REPO
$ virtualenv --python=python3 env
$ source env/bin/activate
$ pip3 install -r requirements.txt
```


### Settings

#### Copy sample settings

```shell
$ cp mochannel/settings.sample.py mochannel/settings.py
```

#### Fill settings

```python
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'your-secret-key'

# Database
DATABASES = {
    ...
}

JWT_AUTH = {
    ...
}
```

### Deployment

```shell
$ source env/bin/activate
$ python3 manage.py runserver 0.0.0.0:8000
```


### API swagger document 

`localhost:8000:/api-doc/`


