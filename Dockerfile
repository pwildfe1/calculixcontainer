FROM fnndsc/ubuntu-python3:ubuntu20.04-python3.8.10

# install Dependencies
RUN apt-get update -y
#RUN apt-get install calculix-ccx -y
RUN apt-get install wget -y
RUN apt install openmpi-bin -y
RUN apt install libgfortran4 -y

WORKDIR root/CalculiX/
RUN wget http://www.dhondt.de/cgx_2.17.1.bz2
RUN wget http://www.dhondt.de/ccx_2.17.tar.bz2
RUN bunzip2 cgx_2.17.1.bz2
RUN tar -xvjf ccx_2.17.tar.bz2 -C ~
RUN chmod +x cgx_2.17.1
RUN chmod +x ccx_2.17/src/ccx_2.17
RUN mv ~/CalculiX/cgx_2.17.1 /usr/local/bin/
RUN mv ~/CalculiX/ccx_2.17/src/ccx_2.17 /usr/local/bin/
RUN ln -s /usr/local/bin/cgx_2.17.1 /usr/local/bin/cgx
RUN ln -s /usr/local/bin/ccx_2.17 /usr/local/bin/ccx

RUN wget http://www.dhondt.de/cgx_2.17.1.htm.tar.bz2
RUN wget http://www.dhondt.de/cgx_2.17.1.exa.tar.bz2
RUN wget http://www.dhondt.de/ccx_2.17.htm.tar.bz2
RUN wget http://www.dhondt.de/ccx_2.17.test.tar.bz2

RUN tar -xvjf cgx_2.17.1.htm.tar.bz2 -C ~ 
RUN tar -xvjf cgx_2.17.1.exa.tar.bz2 -C ~
RUN tar -xvjf ccx_2.17.htm.tar.bz2 -C ~
RUN tar -xvjf ccx_2.17.test.tar.bz2 -C ~
RUN rm *.bz2

# RUN pip3 install --upgrade pip
# RUN pip3 install scikit-image
# RUN pip3 install opencv-python

# copy api scripts
WORKDIR root/api
COPY src /api/src
RUN cp ~/CalculiX/ccx_2.17/test/beamp.inp .
WORKDIR /api

#ENTRYPOINT ["/bin/sh"]
#CMD python3 /api/app.py