PROJECT = slack_pull_reminder
VIRTUAL_ENV = env
FUNCTION_NAME = pull_handler
AWS_REGION = us_west_2
FUNCTION_HANDLER = lamda_handler
LAMBDA_ROLE = arn:aws:iam::179747435213:role/lambda

# default commands

install: virtual
build: clean_package build_package_tmp copy_python remove_unused zip

virtual:
	@echo "--> Setup and activate virtualenv"
	if test ! -d "$(VIRTUAL_ENV)"; then \
		pip install virtualenv; \
		virtualenv $(VIRTUAL_ENV); \
	fi
	@echo ""

clean_package:
	rm -rf ./package/*


build_package_tmp:
	mkdir -p ./package/tmp/lib
	cp -a ./$(PROJECT)/. ./package/tmp/


copy_python:
	if test -d $(VIRTUAL_ENV)/lib; then \
		cp -a $(VIRTUAL_ENV)/lib/python2.7/site-packages/. ./package/tmp; \
	fi

	if test -d $(VIRTUAL_ENV)/lib64; then \
		cp -a $(VIRTUAL_ENV)/lib64/python2.7/site-packages/. ./package/tmp; \
	fi


remove_unused:
	rm -rf ./package/tmp/wheel*
	rm -rf ./package/tmp/easy_install*
	rm -rf ./package/tmp/setuptools*

zip:
	cd ./package/tmp && zip -r ../$(PROJECT).zip . 
