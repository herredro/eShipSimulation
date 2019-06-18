#!/usr/bin/env bash

sudo apt-get install git
git clone https://github.com/herredro/eShipSimulation.git
cd eShipSimulation/
sudo apt install python3-pip
pip3 install simpy
pip3 install numpy
pip3 install colorama
pip3 install tabulate
pip3 install matplotlib

#DOWNLOAD:
# eShipSimulation/csv/out/central_alpha_beta.csv