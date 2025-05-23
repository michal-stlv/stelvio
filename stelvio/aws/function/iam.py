from typing import Any

from pulumi_aws.iam import (
    GetPolicyDocumentStatementArgs,
    GetPolicyDocumentStatementPrincipalArgs,
    Policy,
    Role,
    RolePolicyAttachment,
    get_policy_document,
)

from .constants import LAMBDA_BASIC_EXECUTION_ROLE


def _create_function_policy(name: str, statements: list[dict[str, Any]]) -> Policy | None:
    """Create IAM policy for Lambda if there are any statements."""
    if not statements:
        return None

    policy_document = get_policy_document(statements=statements)
    return Policy(f"{name}-Policy", path="/", policy=policy_document.json)


def _create_lambda_role(name: str) -> Role:
    """Create basic execution role for Lambda."""
    assume_role_policy = get_policy_document(
        statements=[
            GetPolicyDocumentStatementArgs(
                actions=["sts:AssumeRole"],
                principals=[
                    GetPolicyDocumentStatementPrincipalArgs(
                        identifiers=["lambda.amazonaws.com"], type="Service"
                    )
                ],
            )
        ]
    )
    return Role(f"{name}-role", assume_role_policy=assume_role_policy.json)


def _attach_role_policies(name: str, role: Role, function_policy: Policy | None) -> None:
    """Attach required policies to Lambda role."""
    RolePolicyAttachment(
        f"{name}-BasicExecutionRolePolicyAttachment",
        role=role.name,
        policy_arn=LAMBDA_BASIC_EXECUTION_ROLE,
    )
    if function_policy:
        RolePolicyAttachment(
            f"{name}-DefaultRolePolicyAttachment", role=role.name, policy_arn=function_policy.arn
        )
