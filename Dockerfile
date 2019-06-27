FROM python:slim-stretch
MAINTAINER Elyse Morin <elyselouisemorin@gmail.com>
LABEL Description "This App is meant for Yoga Pose prediction from Keras model"

# Update the OS
RUN apt-get update
RUN apt-get install -y gcc

# Copy the files into the container
COPY . /usr/src/app

# Set the working directory
WORKDIR /usr/src/app

# Install the dependencies
RUN pip install Werkzeug Flask numpy Keras gevent pillow h5py tensorflow pandas numpy psycopg2-binary cython
RUN apt-get install -y libsm6 libxext6 libxrender-dev
RUN pip install opencv-python
RUN apt-get install -y libgcc1 llvm
RUN apt-get install -y libglib2.0-0



# Expose the port
EXPOSE 5000

# Run the app
CMD [ "python" , "app.py"]

