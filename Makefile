all: doctor run

doctor:
	@python3 --version

configure:
	@pip3 install -r requirements.txt

run: configure
	@python3 EasyInstall.py