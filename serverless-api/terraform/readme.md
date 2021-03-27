https://www.terraform.io/downloads.html

https://learn.hashicorp.com/tutorials/terraform/install-cli?in=terraform/aws-get-started

Starting

`cd hello_world`

`zip hello_world *.*`

`cd ..`

`aws s3 mb s3://terraform-example-1587`

`aws s3 cp hello_world.zip s3://terraform-example-1587/hello_world.zip`

`terraform init`

`terraform apply`

Clean up

`terraform destroy`
