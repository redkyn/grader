#
# Dockerfile for campus ubuntu version. Latest clang, valgrind, g++, and make.
#
# Welcome to Ubuntu 14.04.3 LTS (GNU/Linux 3.13.0-68-generic x86_64)
FROM ubuntu:14.04.3 
LABEL type=cpp_image_5201
MAINTAINER Billy Rhoades "billyarhoades@gmail.com"

RUN apt-get update
#RUN apt-get upgrade -y
RUN apt-get install -y valgrind clang gcc make python3

ADD payload/* /home/

# Don't allow file modification
RUN chmod -R 555 /home/*

WORKDIR /home
