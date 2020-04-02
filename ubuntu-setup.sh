# ubuntu setup
apt-get update
apt -y install git
apt-get install -y wget unzip curl redis-server

# firefox for selenium dependency
wget https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz
tar -xvzf geckodriver*
mv geckodriver /usr/bin
cd /usr/bin
chmod +x geckodriver
cd
echo 'export PATH="/usr/bin/geckodriver:$PATH"' >> ~/.bashrc

# pyenv - python version and virtualenv manager
curl https://pyenv.run | bash
echo 'export PATH="/home/rcruiksh/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
exec $SHELL
pyenv install 3.8.2
pyenv virtualenv 3.8.2 scheduler
pyenv activate scheduler
pip install --upgrade pip
git clone https://github.com/rcruiksh/chd-schedule.git
cd chd-schedule
pip install -r "requirements.txt"

# running the app
# nohup python manage.py runserver > django.out &
# nuhup redis-server > redis.out &
# nohup celery -A scheduler worker > worker.out &
# nohup celery -A scheduler beat > beat.out &
