#!/bin/sh

python3 -u get_reviews.py
if [ $? -ne 0 ] ; then
    echo "exit code is not 0"
    exit
fi
python3 -u process_reviews.py
python3 -u labels.py

cd ..
git add ./data/reviews.json
git add ./data/labels.json
git commit -m "Data as of $(date)"
git push origin master
cd ./pipeline