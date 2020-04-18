# Info

Manage NS records in target AWS domain

# Requirements

## Terraform

~~~~
terraform version:
Terraform v0.12.24
+ provider.aws v2.57.0
~~~~

# Installation

## Add your AWS key
~~~~
cp provider.tf.example provider.tf
editor provider.tf
~~~~

## Add lambda to zip file

~~~~
zip dns-manager.zip lambda_function.py
~~~~

## Apply

~~~~
terraform apply
~~~~

# Usage

## Info

Check actual API gateway URL [here](https://eu-central-1.console.aws.amazon.com/lambda/home?region=eu-central-1#/functions/dns-manager?tab=configuration)  
Click "API Gateway" icon.

## Add record

~~~~
curl -H "Content-Type: application/json" -d '{"Action": "CREATE", "UserName": "gelo22", "NameServers": "ns-578.awsdns-08.net.,ns-499.awsdns-62.com.,ns-1193.awsdns-21.org.,ns-1715.awsdns-22.co.uk.", "ZoneID": "Z06877161DK1SC4LDL8T3", "DomainName": "cluster.dev", "Email": "gelo@shalb.com"}' https://usgrtk5fqj.execute-api.eu-central-1.amazonaws.com/prod
~~~~

## Update record

~~~~
# curl -H "Content-Type: application/json" -d '{"Action": "UPDATE", "UserName": "gelo22", "NameServers": "ns-578.awsdns-08.net.,ns-499.awsdns-62.com.", "ZoneID": "Z06877161DK1SC4LDL8T3", "DomainName": "cluster.dev", "Email": "gelo@shalb.com"}' https://usgrtk5fqj.execute-api.eu-central-1.amazonaws.com/prod
~~~~

## Delete record

~~~~
# curl -H "Content-Type: application/json" -d '{"Action": "DELETE", "UserName": "gelo22", "ZoneID": "Z06877161DK1SC4LDL8T3", "DomainName": "cluster.dev", "Email": "gelo@shalb.com"}' https://usgrtk5fqj.execute-api.eu-central-1.amazonaws.com/prod
~~~~

