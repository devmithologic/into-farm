provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "my_first_server" {
  ami           = "ami-07ff62358b87c7116"
  instance_type = "t2.micro"

  tags = {
    Name = "terraform-lab-alejandro"
  }
}

output "public_ip" {
  value = aws_instance.my_first_server.public_ip
}