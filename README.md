#VGServer

## install

### Requirements

* Python 2.7

### install Virtualenv

* see [Virtualenv](https://pypi.python.org/pypi/virtualenv)

### Clone from github

```
git clone https://github.com/MobileVG/server.git VGServer
cd VGServer
```

### Install required packages

```
source /your_virtual_env_dir/bin/activate
pip install -r requirements.txt
```

### Create configuration

```
cp config/release.cfg config/debug.cfg

# Modify configuration file
vim config/debug.cfg
```

### Run server

```
python start.py debug
```