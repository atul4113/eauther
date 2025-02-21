# [START dockerfile]
FROM gcr.io/google_appengine/python

# Install the fortunes binary from the debian repositories.
RUN apt-get update && apt-get install -y fortunes
RUN apt-get install pdftk -y
RUN apt-get install inkscape -y
# Python 2.7 == python 2.7.9
RUN virtualenv /env  -p python2.7

# Set virtualenv environment variables. This is equivalent to running
# source /env/bin/activate.
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

ADD requirements.txt /app/
RUN pip install -r requirements.txt
ADD . /app/

#gunicorn
#   -b bind
#   -t timeout for request
#   -w workers
CMD gunicorn -b :$PORT main:app -t 86400 -w 2
# [END dockerfile]
