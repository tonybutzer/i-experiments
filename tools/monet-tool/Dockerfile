FROM python

WORKDIR /home/monet

COPY monet /home/monet/monet
COPY setup.py /home/monet
COPY requirements.txt /home/monet

RUN apt-get update && apt-get install -y python3-pip libgdal-dev locales
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# This will install latest version of GDAL
RUN pip3 install GDAL==3.0.4


RUN pip install -r requirements.txt && python setup.py install





