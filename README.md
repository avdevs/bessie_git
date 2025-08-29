## Local Setup
Make sure you have installed
- MySQL server
- Python environment
- Yarn

Activate your python environment
```
cd bessie
python3 -m venv venv
source venv/bin/activate
```

Once your environment is active, install dependencies:

```
pip3 install -r requirements.txt
```

Run Django
```
python3 manage.py runserver
```
```
python3 manage.py migrate
```