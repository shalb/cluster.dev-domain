# Manage NS records in target AWS domain

## Requirements

* `Terraform` >= 0.12.24

## Installation

### Add your AWS key

```bash
export AWS_ACCESS_KEY_ID='00000000000000000000'
export AWS_SECRET_ACCESS_KEY='0000000000000000000000000000000000000000'
export AWS_DEFAULT_REGION='eu-central-1'
```

### Create S3 bucket

Versioning should be enabled, see [documentation](https://www.terraform.io/docs/backends/types/s3.html)

### Add lambda to zip file

```bash
zip dns-manager.zip lambda_function.py
```

### Apply

```bash
terraform init
terraform apply
```

## Usage

### Info

Check actual API gateway URL [here](https://eu-central-1.console.aws.amazon.com/lambda/home?region=eu-central-1#/functions/dns-manager?tab=configuration).  
Click `API Gateway` icon.

### Add record

```bash
curl -H "Content-Type: application/json" -d '
{
    "Action": "CREATE",
    "UserName": "gelo22",
    "NameServers": "ns-578.awsdns-08.net.,ns-499.awsdns-62.com.,ns-1193.awsdns-21.org.,ns-1715.awsdns-22.co.uk.",
    "ZoneID": "Z06877161DK1SC4LDL8T3",
    "DomainName": "cluster.dev",
    "Email": "gelo@shalb.com"
}
' https://usgrtk5fqj.execute-api.eu-central-1.amazonaws.com/prod
```

### Update record

```bash
curl -H "Content-Type: application/json" -d '
{
    "Action": "UPDATE",
    "UserName": "gelo22",
    "NameServers": "ns-578.awsdns-08.net.,ns-499.awsdns-62.com.",
    "ZoneID": "Z06877161DK1SC4LDL8T3",
    "DomainName": "cluster.dev",
    "Email": "gelo@shalb.com"
}
' https://usgrtk5fqj.execute-api.eu-central-1.amazonaws.com/prod
```

### Delete record

```bash
curl -H "Content-Type: application/json" -d '
{
    "Action": "DELETE",
    "UserName": "gelo22",
    "ZoneID": "Z06877161DK1SC4LDL8T3",
    "DomainName": "cluster.dev",
    "Email": "gelo@shalb.com"
}
' https://usgrtk5fqj.execute-api.eu-central-1.amazonaws.com/prod
```

## Debug

### Logs

See logs [here](https://eu-central-1.console.aws.amazon.com/cloudwatch/home?region=eu-central-1#logStream:group=/aws/lambda/dns-manager;streamFilter=typeLogStreamPrefix).

See filtered exceptions [here](https://eu-central-1.console.aws.amazon.com/cloudwatch/home?region=eu-central-1#logs-insights:queryDetail=~(end~0~start~-518400~timeType~'RELATIVE~unit~'seconds~editorString~'fields*20*40timestamp*2c*20*40message*0a*7c*20filter*20message*3d*22Exception*22*0a*7c*20sort*20*40timestamp*20desc*0a*7c*20limit*2020~isLiveTail~false~queryId~'992e9724-9a6e-4f7a-bc7b-6901e39e723a~source~(~'*2faws*2flambda*2fdns-manager))) (click `Run query`)

### DB records

See DB records [here](https://eu-central-1.console.aws.amazon.com/dynamodb/home?region=eu-central-1#tables:selected=dns-manager;tab=items).


## Terraform

<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|:----:|:-----:|:-----:|
| region | The AWS region. | string | `"eu-central-1"` | no |
| s3\_backend\_bucket | The s3 backend bucket | string | `"dns-manager-state"` | no |

<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->

## Contribute

If you change current code, then you should test it.

Use some separate AWS account for tests, because successful `terraform apply` in working environment is not enough.  
You should apply it from scratch.

Create separate s3 bucket, change it in `terraform.tf`, apply changes.

```bash
editor terraform.tf
terraform init
terraform apply
```

Create and delete test records via API gateway.

