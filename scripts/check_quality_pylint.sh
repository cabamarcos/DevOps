#!/bin/bash

pylint --max-line-length=100 \
       --disable=C0114,C0115,C0116,R1705,C0411 \
       ./movies
