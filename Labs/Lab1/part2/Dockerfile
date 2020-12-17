FROM ubuntu

RUN apt-get update
RUN apt-get -y install bash iproute2 net-tools tcpdump vim iputils-ping
RUN apt-get -y install quagga
RUN apt-get clean

CMD ["bash"]
