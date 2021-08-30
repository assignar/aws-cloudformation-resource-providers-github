# GitHub::Repository::EnvironmentSecret

A secret for a GitHub Repository Environment.

## Syntax

To declare this entity in your AWS CloudFormation template, use the following syntax:

### JSON

<pre>
{
    "Type" : "GitHub::Repository::EnvironmentSecret",
    "Properties" : {
        "<a href="#accesstoken" title="AccessToken">AccessToken</a>" : <i>String</i>,
        "<a href="#owner" title="Owner">Owner</a>" : <i>String</i>,
        "<a href="#repository" title="Repository">Repository</a>" : <i>String</i>,
        "<a href="#environmentname" title="EnvironmentName">EnvironmentName</a>" : <i>String</i>,
        "<a href="#secretname" title="SecretName">SecretName</a>" : <i>String</i>,
        "<a href="#secretvalue" title="SecretValue">SecretValue</a>" : <i>String</i>
    }
}
</pre>

### YAML

<pre>
Type: GitHub::Repository::EnvironmentSecret
Properties:
    <a href="#accesstoken" title="AccessToken">AccessToken</a>: <i>String</i>
    <a href="#owner" title="Owner">Owner</a>: <i>String</i>
    <a href="#repository" title="Repository">Repository</a>: <i>String</i>
    <a href="#environmentname" title="EnvironmentName">EnvironmentName</a>: <i>String</i>
    <a href="#secretname" title="SecretName">SecretName</a>: <i>String</i>
    <a href="#secretvalue" title="SecretValue">SecretValue</a>: <i>String</i>
</pre>

## Properties

#### AccessToken

GitHub Access Token

_Required_: Yes

_Type_: String

_Pattern_: <code>^[0-9a-zA-Z-_]*$</code>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### Owner

The name of the repository owner.

_Required_: Yes

_Type_: String

_Maximum_: <code>39</code>

_Pattern_: <code>^[0-9a-zA-Z-]*$</code>

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### Repository

The name of the repository.

_Required_: Yes

_Type_: String

_Maximum_: <code>100</code>

_Pattern_: <code>^[0-9a-zA-Z-]*$</code>

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### EnvironmentName

The name of the environment.

_Required_: Yes

_Type_: String

_Maximum_: <code>255</code>

_Pattern_: <code>^[0-9a-zA-Z-]*$</code>

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### SecretName

The name of the secret.

_Required_: Yes

_Type_: String

_Maximum_: <code>255</code>

_Pattern_: <code>^[0-9a-zA-Z-]*$</code>

_Update requires_: [Replacement](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-replacement)

#### SecretValue

The name of the secret.

_Required_: Yes

_Type_: String

_Maximum_: <code>65535</code>

_Pattern_: <code>^[0-9a-zA-Z-]*$</code>

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

