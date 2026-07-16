"""Networking resources: default VPC lookup, subnet group and security group."""

from dataclasses import dataclass
from typing import Any

import pulumi_aws as aws


@dataclass(frozen=True)
class NetworkResources:
    vpc: Any
    subnet_group: aws.rds.SubnetGroup
    security_group: aws.ec2.SecurityGroup


def create_network(account_id: str, db_port: int = 3306) -> NetworkResources:
    """Create the RDS subnet group and security group in the account's default VPC."""
    default_vpc = aws.ec2.get_vpc(default=True)
    default_subnets = aws.ec2.get_subnets(
        filters=[aws.ec2.GetSubnetsFilterArgs(name="vpc-id", values=[default_vpc.id])]
    )

    subnet_group = aws.rds.SubnetGroup(
        "mysql-subnet-group",
        subnet_ids=default_subnets.ids,
        tags={"Name": f"mysql-subnet-group-{account_id}"},
    )

    security_group = aws.ec2.SecurityGroup(
        "mysql-sg",
        vpc_id=default_vpc.id,
        description="Allow MySQL access",
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=db_port,
                to_port=db_port,
                cidr_blocks=[default_vpc.cidr_block],
            )
        ],
        egress=[
            aws.ec2.SecurityGroupEgressArgs(
                protocol="-1",
                from_port=0,
                to_port=0,
                cidr_blocks=["0.0.0.0/0"],
            )
        ],
        tags={"Name": f"mysql-sg-{account_id}"},
    )

    return NetworkResources(
        vpc=default_vpc,
        subnet_group=subnet_group,
        security_group=security_group,
    )
