"""RDS MySQL instance resource."""

import pulumi_aws as aws

from lib.config import DbConfig
from lib.network import NetworkResources


def create_mysql_instance(
    db_config: DbConfig,
    network: NetworkResources,
    account_id: str,
) -> aws.rds.Instance:
    """Create the RDS MySQL instance using the given config and network resources."""
    return aws.rds.Instance(
        "mysql-instance",
        engine="mysql",
        engine_version=db_config.engine_version,
        instance_class=db_config.instance_class,
        allocated_storage=db_config.allocated_storage,
        db_name=db_config.name,
        username=db_config.username,
        password=db_config.password,
        db_subnet_group_name=network.subnet_group.name,
        vpc_security_group_ids=[network.security_group.id],
        publicly_accessible=False,
        skip_final_snapshot=True,
        apply_immediately=db_config.apply_immediately,
        tags={"Name": f"mysql-instance-{account_id}"},
    )
