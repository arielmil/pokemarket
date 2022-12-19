#!/bin/bash

cd pokemarket/utils/pythonContainerFiles

python3 createCriptoKey.py

cd ../../app

flask run
