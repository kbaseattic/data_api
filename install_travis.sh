#!/usr/bin/env bash

if [[ THRIFT_CACHED -eq 0 ]] ; then
    apt-get update -qq
    apt-get install -qq libboost-dev libboost-test-dev \
libboost-program-options-dev libevent-dev automake libtool \
flex bison pkg-config g++ libssl-dev \
libbit-vector-perl libclass-accessor-class-perl
    mkdir $HOME/thrift && cd $HOME/thrift
    wget http://www.us.apache.org/dist/thrift/0.9.2/thrift-0.9.2.tar.gz
    tar xfz thrift-0.9.2.tar.gz
    cd thrift-0.9.2
    ./configure --without-ruby
    make install
    cd -
elif [[ THRIFT_CACHED -eq 1 ]] ; then
    cd $HOME/thrift/thrift-0.9.2/
    ./configure --without-ruby
    make install
    cd -
fi
