# bash init.sh

# drop all db table
#./manage.py sqlclear packagename | ./manage.py dbshell

python manage.py makemigrations example
python manage.py migrate example --noinput

python manage.py migrate sites --noinput
python manage.py migrate auth --noinput
python manage.py migrate contenttypes --noinput

python manage.py migrate --noinput

# preload critical data
python manage.py loaddata ./data/fixtures/sites.json
python manage.py loaddata ./data/fixtures/groups.json
# python manage.py loaddata ./data/fixtures/users.json
