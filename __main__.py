"""An AWS Python Pulumi program - MySQL RDS instance"""

import pulumi
import pulumi_aws as aws

config = pulumi.Config()

# --- Configurable inputs ---
# Change `db_engine_version` and run `pulumi preview` / `pulumi up` to test a new
# engine version. Use `pulumi refresh --diff` beforehand to check for drift
# against the real infrastructure before applying changes.
db_engine_version = config.get("dbEngineVersion") or "8.0.35"
db_instance_class = config.get("dbInstanceClass") or "db.t3.micro"
db_allocated_storage = config.get_int("dbAllocatedStorage") or 20
db_name = config.get("dbName") or "appdb"
db_username = config.get("dbUsername") or "admin"
db_password = config.require_secret("dbPassword")
apply_immediately = config.get_bool("applyImmediately")
if apply_immediately is None:
    apply_immediately = True

current_identity = aws.get_caller_identity()
account_id = current_identity.account_id

# --- Networking: use the default VPC + its subnets ---
default_vpc = aws.ec2.get_vpc(default=True)
default_subnets = aws.ec2.get_subnets(
    filters=[aws.ec2.GetSubnetsFilterArgs(name="vpc-id", values=[default_vpc.id])]
)

db_subnet_group = aws.rds.SubnetGroup(
    "mysql-subnet-group",
    subnet_ids=default_subnets.ids,
    tags={"Name": f"mysql-subnet-group-{account_id}"},
)

db_security_group = aws.ec2.SecurityGroup(
    "mysql-sg",
    vpc_id=default_vpc.id,
    description="Allow MySQL access",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=3306,
            to_port=3306,
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

# --- RDS MySQL instance ---
mysql_instance = aws.rds.Instance(
    "mysql-instance",
    engine="mysql",
    engine_version=db_engine_version,
    instance_class=db_instance_class,
    allocated_storage=db_allocated_storage,
    db_name=db_name,
    username=db_username,
    password=db_password,
    db_subnet_group_name=db_subnet_group.name,
    vpc_security_group_ids=[db_security_group.id],
    publicly_accessible=False,
    skip_final_snapshot=True,
    apply_immediately=apply_immediately,
    tags={"Name": f"mysql-instance-{account_id}"},
)

pulumi.export("db_endpoint", mysql_instance.endpoint)
pulumi.export("db_address", mysql_instance.address)
pulumi.export("db_port", mysql_instance.port)
pulumi.export("db_engine_version", mysql_instance.engine_version)
