# GitHub Resource Providers for AWS CloudFormation

## Overview

| Resource Name | Directory | Description |
| ---                                   | ---  | ---         |
| `GitHub::Repository::Environment` | `./github-repository-environment` | Creates GitHub Environments.|
| `GitHub::Repository::EnvironmentSecret` | `./github-repository-environment-secret ` | Creates Secrets for GitHub Environments. |

## Installation

Each resource needs to be installed separately.

1. Enter resource directory

```bash
cd ./github-repository-environment
```

2. Install resource with [CloudFormation CLI](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-using-cli.html)

```
cfn submit --set-default
```

## Example CloudFormation Template

The example below can be used with [Personal Access Tokens](https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token).

```
Resources:
  Environment:
    Type: GitHub::Repository::Environment
    Properties:
      AccessToken: "MY_GITHUB_TOKEN"
      Owner: "octocat"
      Repository: "hello-world"
      EnvironmentName: "example"
  EnvironmentSecret:
    Type: GitHub::Repository::EnvironmentSecret
    DependsOn:
      - Environment
    Properties:
      AccessToken: "MY_GITHUB_TOKEN"
      Owner: "octocat"
      Repository: "hello-world"
      EnvironmentName: "example"
      SecretName: "EXAMPLE_SECRET"
      SecretValue: "EXAMPLE_SECRET_VALUE"
```