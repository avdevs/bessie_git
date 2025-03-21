# NOTE: COPIED FROM ANOTHER DJANGO PROJECT, NEEDS ADJUSTING/UPDATING

## Installation

Follow below steps to install the project locally on your computer.

### Dependencies
Make sure you have installed on your system:

- MySQL server - [Installation steps](https://bitjamlabs.co.uk/bitjam/bitjam-wikis/-/wikis/MySQL-local-install-and-setup)
- Redis server - [Installation steps](https://bitjamlabs.co.uk/bitjam/bitjam-wikis/-/wikis/Redis-local-install-and-setup)
- Python environment - [Setup steps](https://bitjamlabs.co.uk/bitjam/bitjam-wikis/-/wikis/Python-virtual-environments)
- Yarn - to manage node modules. [Setup](https://bitjamlabs.co.uk/bitjam/bitjam-wikis/-/wikis/Yarn)

### Project setup
Clone this repository to your local computer by issuing `git clone git@bitjamlabs.co.uk:bitjam/bessie.git`.

Once downloaded enter directory, create and activate python environment:


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
Your python env needs to be enabled for this.

Start the project
```
./exec run
```

In another tab
```
./exec migrate
```

#### JS specific
This projects styles are built using Sass, therefore those files have to compiled to CSS so the browser can understand it.

First install [gulpjs](https://gulpjs.com) globally: `sudo yarn global add gulp`.

When you are in project root, execute `yarn install`.
Currently this will install 3 packages:
- gulp - a task runner that will run 2 below packages,
- gulp-sass - Sass to CSS compiler
- browser-sync - a package that can refresh browser when you make project changes