all: pkg get-tf uz
pkg:
	sudo yum update
	sudo yum install wget unzip -y


get-tf:
	wget https://releases.hashicorp.com/terraform/0.12.24/terraform_0.12.24_linux_amd64.zip


uz:
	sudo unzip terraform_0.12.24_linux_amd64.zip -d /usr/local/bin/
