# Pull base image
FROM resin/raspberry-pi-alpine
MAINTAINER Hugo Larcher <hugo.larcher@gmail.com>

# Install dependencies
RUN apt-get update && apt-get install -y \
    python \
    python-dev \
    python-pip \
    python-virtualenv \
    build-essential \
    i2c-tools \
    libi2c-dev \
    python-smbus\
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

ADD edf.py /data/

# Define working directory
WORKDIR /data

# Install dependencies
RUN pip install pymongo pyparsing RPi.GPIO pyserial

# Define entry point
ENTRYPOINT ["python"]

# Define default command
CMD ["edf.py"]
