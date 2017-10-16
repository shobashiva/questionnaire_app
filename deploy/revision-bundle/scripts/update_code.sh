#!/bin/bash

cd /home/ubuntu
source env/bin/activate
cd pcusa-comms-process-observation

git pull
pip install --exists-action w -r requirements.txt

# compress and uglify css, js, etc.
cd base/static
npm install
gulp build
cd ../..

./manage.py syncdb
echo 'yes' | ./manage.py collectstatic

