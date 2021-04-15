# set base image (host OS)
FROM python:3.8

# set the working directory in the container
WORKDIR /code

# # install dependencies
# RUN pip install -U pip setuptools wheel
# RUN pip install -U spacy
# RUN python -m spacy download en_core_web_sm

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY src/ .

# command to run on container start
CMD [ "python", "./worker.py" ]