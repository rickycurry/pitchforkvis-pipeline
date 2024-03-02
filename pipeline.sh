#!/bin/sh

python3 -u get_reviews.py
if [ $? -ne 0 ] ; then
    echo "exit code is not 0"
    exit
fi
python3 -u process_reviews.py