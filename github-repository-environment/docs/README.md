# GitHub::Repository::Environment

An Environment for a GitHub Repository.

## Syntax

To declare this entity in your AWS CloudFormation template, use the following syntax:

### JSON

<pre>
{
    "Type" : "GitHub::Repository::Environment",
    "Properties" : {
        "<a href="#accesstoken" title="AccessToken">AccessToken</a>" : <i>String</i>,
        "<a href="#owner" title="Owner">Owner</a>" : <i>String</i>,
        "<a href="#repository" title="Repository">Repository</a>" : <i>String</i>,
        "<a href="#environmentname" title="EnvironmentName">EnvironmentName</a>" : <i>String</i>,
        "<a href="#waittimer" title="WaitTimer">WaitTimer</a>" : <i>Integer</i>,
        "<a href="#reviewers" title="Reviewers">Reviewers</a>" : <i>[ String, ... ]</i>,
    }
}
</pre>

### YAML

<pre>
Type: GitHub::Repository::Environment
Properties:
    <a href="#accesstoken" title="AccessToken">AccessToken</a>: <i>String</i>
    <a href="#owner" title="Owner">Owner</a>: <i>String</i>
    <a href="#repository" title="Repository">Repository</a>: <i>String</i>
    <a href="#environmentname" title="EnvironmentName">EnvironmentName</a>: <i>String</i>
    <a href="#waittimer" title="WaitTimer">WaitTimer</a>: <i>Integer</i>
    <a href="#reviewers" title="Reviewers">Reviewers</a>: <i>
      - String</i>
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

#### WaitTimer

The amount of time to delay a job after the job is initially triggered in minutes.

_Required_: No

_Type_: Integer

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### Reviewers

The people or teams that may review jobs that reference the environment. Maximum six.

_Required_: No

_Type_: List of String

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

## Return Values

### Fn::GetAtt

The `Fn::GetAtt` intrinsic function returns a value for a specified attribute of this type. The following are the available attributes and sample return values.

For more information about using the `Fn::GetAtt` intrinsic function, see [Fn::GetAtt](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html).

#### Id

GitHub environment ID

#### Url

GitHub environment URL

