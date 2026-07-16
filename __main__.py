"""An AWS Python Pulumi program - MySQL RDS instance"""

import pulumi
import pulumi_aws as aws

from lib.config import load_db_config
from lib.database import create_mysql_instance
from lib.network import create_network

db_config = load_db_config()

current_identity = aws.get_caller_identity()
account_id = current_identity.account_id

network = create_network(account_id)

mysql_instance = create_mysql_instance(db_config, network, account_id)

pulumi.export("db_endpoint", mysql_instance.endpoint)
pulumi.export("db_address", mysql_instance.address)
pulumi.export("db_port", mysql_instance.port)
pulumi.export("db_engine_version", mysql_instance.engine_version)
