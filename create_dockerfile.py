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

# Install updates and required softwares
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y sudo vim

RUN mkdir /appuser
RUN groupadd -g 701 -r appuser && useradd -r -u 701 -g appuser -d /home/appuser -s /bin/bash -m appuser
RUN echo "appuser ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
RUN echo "Defaults:appuser !requiretty" >> /etc/sudoers

USER appuser

RUN sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 561F9B9CAC40B2F7
RUN sudo apt-get install -y apt-transport-https ca-certificates

RUN sudo sh -c 'echo deb https://oss-binaries.phusionpassenger.com/apt/passenger jessie main > /etc/apt/sources.list.d/passenger.list' && sudo apt-get update

RUN sudo apt-get install -y --no-install-recommends nodejs \
build-essential libpq-dev nano mysql-client postgresql-client \
sqlite3 ghostscript apache2 apache2-mpm-worker libcurl4-openssl-dev \
apache2-threaded-dev libapr1-dev libaprutil1-dev libapache2-mod-passenger

RUN sudo gem install rails --version "$RAILS_VERSION"

RUN sudo sh -c 'echo sudo /usr/sbin/apachectl restart > /etc/bash.bashrc'

RUN sudo apachectl restart

# Set user environment
RUN sudo mkdir /rails
RUN sudo mkdir /rails/$APP_DIR
RUN sudo chown -R appuser:appuser /appuser
VOLUME ["/rails/$APP_DIR"]
WORKDIR /rails/$APP_DIR

USER root
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
</VirtualHost>" > /etc/apache2/sites-enabled/000-default.conf

USER appuser

CMD sudo a2enmod passenger && sudo apache2ctl restart && sudo /bin/bash
"""

  with open('Dockerfile', 'w') as f:
    f.write(dockerfile_template.format(**variables))

if __name__ == "__main__":
  main()
