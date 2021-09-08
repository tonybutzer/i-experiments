variable "region" {
  description = "The AWS region."
  default = "us-west-2"
}

variable "master_instance_type" {
  description = "The instance type."
  default = "t3a.large"
}

variable "ship_instance_type" {
  description = "ships - The instance type."
  # default = "c5.9xlarge"
  default = "t3a.2xlarge"
}


variable "subnet_id" {
  description = "The AWS network id representing the allowed vpc"
  # internal-Subnet-B
  default = "subnet-06cf6942c47c4958d"
}

variable "ship_userdata" {
  description = "user data os startup scripts"
  default = ["ship0.sh", "ship1.sh"]
}

variable "ship_name" {
  description = "ship names - DUH!"
  default = ["butzer-lsds-iarpa1", "butzer-sship-1"]
}
variable "test_name" {
  description = "The test number"
  default = "a1"
}

variable "key_name" {
  description = "The AWS key pair to use for resources."
  default = "CHS-LSDSDPAS-butzer"
}

variable "ami" {
  description = "AMI"
  default = "ami-0c2d06d50ce30b442"
}

variable "security_group_ssh" {
  description = "The AWS security group id"
  default = "sg-0b6628f01870c90ed"
}

variable "iam_role" {
  description = "The AWS iam role"
  default = "lsds-developer-ec2"
}

