# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory in the container to /app
WORKDIR /compare-pdfs

# Add the current directory contents into the container at /app
ADD app /compare-pdfs/app

ADD requirements.txt /compare-pdfs
ADD app.py /compare-pdfs

# install dependencies
RUN pip install --upgrade pip
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir /compare-pdfs/uploader-folder

EXPOSE 5000

CMD ["python", "app.py"]
