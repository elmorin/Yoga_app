FROM python:slim-stretch
MAINTAINER Elyse Morin <elyselouisemorin@gmail.com>
LABEL Description "This App is meant for Yoga Pose prediction from Keras model"

# Update the OS
RUN apt-get update

# Copy the files into the container
COPY . /usr/src/app

# Set the working directory
WORKDIR /usr/src/app

# Install the dependencies
RUN pip install Werkzeug Flask numpy Keras gevent pillow h5py tensorflow pandas numpy conda psycopg2-binary cython
RUN conda install opencv llvm gcc libgcc

# Expose the port
EXPOSE 5000

# Run the app
CMD [ "python" , "app.py"]

