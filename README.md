## Installation

Follow below steps to install the project locally on your computer.

### Dependencies

Make sure you have installed on your system:

- MySQL server
- Redis server
- Python environment
- Yarn

#### Python specific

```
cd bessie
python3 -m venv venv
source venv/bin/activate
```

Once your environment is active, install python dependencies:

```
pip3 install -r requirements.txt
```

#### Django specific
```
./exec run
```
```
./exec migrate
```

#### JS specific
This projects styles are built using Sass, therefore those files have to compiled to CSS so the browser can understand it.

First install gulpjs `sudo yarn global add gulp`.

Then `yarn install`.