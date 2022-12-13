apt-get update
apt-get install python3-distutils -y

cd ../app/controller

python3 -m venv env
source env/bin/activate

python3 disutils get-pip.py
pip install --upgrade pip
pip install Cmake psycopg2-binary Flask>=2.0.2 Flask-Session setuptools_rust cryptography pathlib

export FLASK_APP=base.py

python3 utils/createCritoKey.py
