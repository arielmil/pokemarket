FROM python
ENV FLASK_APP base.py
RUN apt-get update
RUN apt-get install python3-distutils -y

RUN git clone https://github.com/arielmil/pokemarket.git

RUN pip install --upgrade pip
RUN pip install Cmake psycopg2-binary Flask>=2.0.2 Flask-Session Flask-Login setuptools_rust cryptography pathlib

ENV FLASK_APP base.py

COPY utils/pythonContainerFiles/start.sh .

COPY utils/pythonContainerFiles/start.sh .

RUN chmod +x start.sh

ENTRYPOINT ["./start.sh"]
