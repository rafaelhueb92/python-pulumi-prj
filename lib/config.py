"""Centralized Pulumi configuration for the RDS MySQL stack."""

from dataclasses import dataclass

import pulumi


@dataclass(frozen=True)
class DbConfig:
    engine_version: str
    instance_class: str
    allocated_storage: int
    name: str
    username: str
    password: pulumi.Output[str]
    apply_immediately: bool


def load_db_config() -> DbConfig:
    """Read and validate all `dbXxx` config values, applying defaults."""
    config = pulumi.Config()

    apply_immediately = config.get_bool("applyImmediately")
    if apply_immediately is None:
        apply_immediately = True

    return DbConfig(
        engine_version=config.get("dbEngineVersion") or "8.0.43",
        instance_class=config.get("dbInstanceClass") or "db.t3.micro",
        allocated_storage=config.get_int("dbAllocatedStorage") or 20,
        name=config.get("dbName") or "appdb",
        username=config.get("dbUsername") or "admin",
        password=config.require_secret("dbPassword"),
        apply_immediately=apply_immediately,
    )
