# -*- coding: utf-8 -*-

# 
# Script to create a base Rails Docker image
# 
# Arguments:
#   * Ruby version
#   * Rails version
#

import sys

def main():

  variable_keys = ["ruby_version", "rails_version"]

  # Error handling and example usage
  if len(sys.argv)-1 != len(variable_keys):
    print "\nDockerfile script\nERROR: Wrong number of arguments. Expected number ", len(variable_keys)
    print "\nOrder of the arguments"
    for v in variable_keys:
      print '\t',v
    print "\nExample usage to create a Dockerfile with ruby version 2.0 and rails version 3.2.19:"
    print "$ python create_dockerfile.py 2.0 3.2.19\n"
    sys.exit(-1)

  # Create dictionary with variable names and command line arguments
  # First command line argument is ignored because references file name.
  variables = dict(zip(variable_keys, sys.argv[1:]))

  # Dockerfile template for Ubuntu with rails
  dockerfile_template = """FROM ruby:{ruby_version}

MAINTAINER Hitabis info@hitabis.de

ENV RAILS_VERSION {rails_version}
ENV APP_DIR app
# Adds nano text editor
ENV TERM xterm

# Update
RUN apt-get update

# install rails ------------------------------------------------ >>

RUN apt-get install -y nodejs build-essential nodejs libpq-dev nano mysql-client postgresql-client sqlite3 ghostscript --no-install-recommends

RUN gem install rails --version "$RAILS_VERSION"

# apache setup ---------------------------------------------------

# Apache
RUN apt-get -y install apache2 apache2-mpm-worker

RUN echo '/usr/sbin/apachectl restart' >> /etc/bash.bashrc

RUN apachectl restart

# Set user environment
RUN mkdir /rails
RUN mkdir /rails/$APP_DIR
VOLUME ["/rails/$APP_DIR"]
WORKDIR /rails/$APP_DIR

RUN mkdir /guest
RUN groupadd -r guest && useradd -r -g guest -d /home/guest -s /bin/bash -m guest
RUN chown -R guest:guest /rails

# passenger dependencies --------------------------------------------- >>

RUN apt-get install -y nodejs --no-install-recommends

# Curl development headers with SSL support
RUN apt-get install -y libcurl4-openssl-dev

# Apache 2 development headers
RUN apt-get install -y apache2-threaded-dev

# Apache Portable Runtime (APR) development headers
RUN apt-get install -y libapr1-dev

# Apache Portable Runtime Utility (APU) development headers
RUN apt-get install -y libaprutil1-dev

# install passenger ---------------------------------------------------- >>

# Install our PGP key and add HTTPS support for APT
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 561F9B9CAC40B2F7
RUN apt-get install -y apt-transport-https ca-certificates

# Add our APT repository
RUN sh -c 'echo deb https://oss-binaries.phusionpassenger.com/apt/passenger jessie main > /etc/apt/sources.list.d/passenger.list'
RUN apt-get update

# Install Passenger + Apache module
RUN apt-get install -y libapache2-mod-passenger

RUN chsh -s /bin/bash root
RUN echo 'ServerName localhost' >> /etc/apache2/apache2.conf

RUN a2enmod passenger
RUN apache2ctl restart

# config passenger ----------------------------------------------------- >>
RUN echo "<VirtualHost *:80>\\n \  
  # ServerName localhost\\n \  
  DocumentRoot /rails/$APP_DIR/public\\n \  
  <Directory /rails/$APP_DIR/public>\\n \  
    # This relaxes Apache security settings.\\n \  
    AllowOverride all\\n \  
    # MultiViews must be turned off.\\n \  
    Options -MultiViews\\n \  
    # Uncomment this if you're on Apache >= 2.4:\\n \  
    Require all granted\\n \  
    RailsEnv development\\n \  
  </Directory>\\n \  
</VirtualHost>  " > /etc/apache2/sites-enabled/000-default.conf
"""

  with open('Dockerfile', 'w') as f:
    f.write(dockerfile_template.format(**variables))

if __name__ == "__main__":
  main()
