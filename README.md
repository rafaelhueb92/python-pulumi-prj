# 🚀 AWS Python MySQL RDS Pulumi Template

[![Pulumi CI/CD](https://github.com/rafaelhueb92/python-pulumi-prj/actions/workflows/pulumi.yml/badge.svg)](https://github.com/rafaelhueb92/python-pulumi-prj/actions/workflows/pulumi.yml)
[![Pulumi](https://img.shields.io/badge/Pulumi-IaC-8A3391?logo=pulumi&logoColor=white)](https://www.pulumi.com/)
[![Python](https://img.shields.io/badge/Python-3.6%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![AWS](https://img.shields.io/badge/AWS-RDS%20%7C%20EC2-FF9900?logo=amazonaws&logoColor=white)](https://aws.amazon.com/)
[![OIDC](https://img.shields.io/badge/Auth-GitHub%20OIDC-2088FF?logo=githubactions&logoColor=white)](https://github.com/rafaelhueb92/oidc-github-actions-role-aws/)

A Pulumi template for provisioning a MySQL RDS instance on AWS using Python, with a GitHub Actions CI/CD workflow.

## 📖 Overview

This template provisions:

- An `aws.rds.SubnetGroup` and `aws.ec2.SecurityGroup` in the account's default VPC.
- An `aws.rds.Instance` running MySQL, with the engine version, instance class, storage and credentials driven by Pulumi config.

## ✅ Prerequisites

- An AWS account with permissions to create RDS, EC2 (VPC/SG) resources.
- AWS credentials configured in your environment (for example via AWS CLI or environment variables).
- Python 3.6 or later installed.
- Pulumi CLI already installed and logged in.

## 🏁 Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Select/create the stack:
   ```bash
   pulumi stack select dev
   ```
3. Set the DB master password as a secret (required, not stored in plain config):
   ```bash
   pulumi config set --secret dbPassword <your-password>
   ```
4. Preview the planned changes:
   ```bash
   pulumi preview
   ```
5. Deploy the stack:
   ```bash
   pulumi up
   ```
6. Tear down when finished:
   ```bash
   pulumi destroy
   ```

## 🗂️ Project Layout

```
├── __main__.py                     # Entry point: orchestrates config/network/database modules
├── config.py                       # Loads and validates Pulumi config (DbConfig)
├── network.py                      # Default VPC lookup, RDS subnet group, security group
├── database.py                     # RDS MySQL instance resource
├── Pulumi.yaml                     # Project metadata and template configuration
├── Pulumi.<stack>.yaml             # Stack-specific configuration (e.g., Pulumi.dev.yaml)
├── requirements.txt                # Python dependencies
└── .github/workflows/pulumi.yml    # CI/CD workflow (preview/up/destroy)
```

## ⚙️ Configuration

| Key                   | Description                               | Default        |
| --------------------- | ----------------------------------------- | -------------- |
| `aws:region`          | AWS region to deploy into                 | `us-east-1`    |
| `dbEngineVersion`     | MySQL engine version                      | `8.0.35`       |
| `dbInstanceClass`     | RDS instance class                        | `db.t3.micro`  |
| `dbAllocatedStorage`  | Allocated storage in GB                   | `20`           |
| `dbName`              | Initial database name                     | `appdb`        |
| `dbUsername`          | Master username                           | `admin`        |
| `dbPassword` (secret) | Master password — must be set as a secret | none, required |
| `applyImmediately`    | Apply changes (e.g. version) immediately  | `true`         |

View or update configuration with:

```bash
pulumi config get dbEngineVersion
pulumi config set dbEngineVersion 8.0.39
```

## 🔍 Testing a New Engine Version & Checking Drift

1. Before changing anything, refresh Pulumi's state against the real infrastructure and review any drift:
   ```bash
   pulumi refresh --diff
   ```
2. Set the new engine version you want to test:
   ```bash
   pulumi config set dbEngineVersion 8.0.39
   ```
3. Preview the change to confirm only the engine version (and any drifted attributes) will be updated:
   ```bash
   pulumi preview --diff
   ```
4. Apply it:
   ```bash
   pulumi up
   ```
5. After testing, re-run `pulumi refresh --diff` again to confirm the live instance now matches the desired state and there is no further drift.

## 📤 Outputs

Once deployed, the stack exports:

- `db_endpoint` — the connection endpoint (host:port) of the RDS instance.
- `db_address` — the hostname of the RDS instance.
- `db_port` — the port of the RDS instance.
- `db_engine_version` — the engine version currently applied.

Retrieve outputs with:

```bash
pulumi stack output db_endpoint
```

## 🔄 CI/CD: GitHub Actions

The workflow at `.github/workflows/pulumi.yml` runs on:

- `push` to `main` → `pulumi up`
- `pull_request` targeting `main` → `pulumi preview`
- `workflow_dispatch` (manual run) → `pulumi up`, unless the `destroy` input is set to `true`, in which case it runs `pulumi destroy`. The `destroy` input defaults to `false`.

### 🔐 Required GitHub secrets

AWS authentication uses OIDC — GitHub Actions assumes an IAM role via short-lived tokens, no long-lived AWS access keys are stored.

The IAM role and OIDC provider assumed by this workflow are created using the [oidc-github-actions-role-aws](https://github.com/rafaelhueb92/oidc-github-actions-role-aws/) repo.

| Secret                | Purpose                                   |
| --------------------- | ----------------------------------------- |
| `PULUMI_ACCESS_TOKEN` | Pulumi Cloud access token (state backend) |

The workflow requests `id-token: write` permission and calls `aws-actions/configure-aws-credentials` with:

```yaml
role-to-assume: arn:aws:iam::263015886492:role/GitHubActionsRole-${{ github.event.repository.name }}
```

The account ID (`263015886492`) was resolved with `aws sts get-caller-identity` against the account this project deploys to, and is hardcoded directly in the workflow rather than stored as a secret (account IDs aren't sensitive). The repository name (without the org/owner) comes automatically from `github.event.repository.name`. This assumes the IAM role is named `GitHubActionsRole-<repo-name>` — create it with that name, or adjust the expression to match your naming convention. If you deploy this to a different AWS account, update the account ID accordingly (re-run `aws sts get-caller-identity` to get the new value).

The role must trust GitHub's OIDC provider (`token.actions.githubusercontent.com`) and be scoped (via its trust policy `sub` condition) to this repository, e.g.:

```json
{
  "Effect": "Allow",
  "Principal": {
    "Federated": "arn:aws:iam::<ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
  },
  "Action": "sts:AssumeRoleWithWebIdentity",
  "Condition": {
    "StringEquals": {
      "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
    },
    "StringLike": {
      "token.actions.githubusercontent.com:sub": "repo:<ORG>/<REPO>:*"
    }
  }
}
```

The role's permission policy needs RDS, EC2 (VPC/SG/subnets) and STS `GetCallerIdentity` permissions.

The `dbPassword` secret must already be set in the stack config (`pulumi config set --secret dbPassword ...`) and committed as an encrypted value in `Pulumi.dev.yaml`, since it is a required Pulumi config secret rather than a GitHub secret.

To manually trigger a destroy from GitHub: go to **Actions → Pulumi RDS Deployment → Run workflow**, and set the `destroy` input to `true`.

## 💬 Help and Community

If you have questions or need assistance:

- Pulumi Documentation: https://www.pulumi.com/docs/
- Community Slack: https://slack.pulumi.com/
- GitHub Issues: https://github.com/pulumi/pulumi/issues

Contributions and feedback are always welcome! 🎉
