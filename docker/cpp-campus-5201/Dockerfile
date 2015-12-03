#
# Dockerfile for campus ubuntu version. Latest clang, valgrind, g++, and make.
#
# Welcome to Ubuntu 14.04.3 LTS (GNU/Linux 3.13.0-68-generic x86_64)
FROM ubuntu:14.04.3 
LABEL type=cpp_image_5201
MAINTAINER Billy Rhoades "billyarhoades@gmail.com"

RUN apt-get update
RUN apt-get upgrade -y
RUN locale-gen
RUN apt-get install -y valgrind clang gcc make python3 vim git zsh wget \
  python3-dev curl cmake python-dev

RUN useradd -ms `which zsh` grader; chown -R grader /home/grader; chmod -R 755\
 /home/grader

ENV HOME /home/grader
USER grader

# Setup zsh
RUN \
  zsh -c 'git clone --recursive https://github.com/garbin/prezto.git "${ZDOTDIR:-$HOME}/.zprezto"; setopt EXTENDED_GLOB;  for rcfile in "${ZDOTDIR:-$HOME}"/.zprezto/runcoms/^README.md(.N); do ln -s "$rcfile" "${ZDOTDIR:-$HOME}/.${rcfile:t}";  done'

RUN echo "BYE"
# Setup vim / zsh config
RUN mkdir ${HOME}/libs; git clone https://github.com/brhoades/dotconfigs.git ~/libs/dotfiles;\
 rm -rf ${HOME}/.zprezto; ln -s ${HOME}/libs/dotfiles/dotzprezto ${HOME}/.zprezto; sh ~/libs/dotfiles/dotvim/setup.sh


USER root

ADD payload /home/grader/files/

# Don't allow file modification
RUN chmod -R 555 /home/grader/files; chown -R nobody.nogroup /home/grader/files; mv /home/grader/files/* /home/grader

USER grader

WORKDIR /home/grader
