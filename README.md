ensure you're in /amazon folder

Check the version of Python you have installed:
python3 -V
Python 3.6.7

Next, install pip from the official repositories:
sudo apt install python3-pip

Install the venv package to create your virtual environment:
sudo apt install python3-venv
sudo python3 -m virtualenv env

source env/bin/activate (активирует виртуальное окружение)

sudo mv chromedriver /usr/bin/
sudo chmod 777 /usr/bin/chromedriver

run main.py
