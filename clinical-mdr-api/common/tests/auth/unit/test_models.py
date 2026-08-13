from typing import Any

import pytest

from common.auth.dependencies import dummy_user
from common.auth.models import AccessTokenClaims, User
from common.exceptions import ForbiddenException

user_obj = dummy_user()


def test_user_model_constructor():
    data: dict[str, Any] = {
        "sub": "xyz",
        "azp": "unknown-user",
        "oid": "unknown-user",
        "name": "John Doe",
        "username": "john@example.com",
        "email": "john@example.com",
        "roles": {"Study.Read", "Library.Write", "a"},
    }
    _user = User(
        sub=data["sub"],
        azp=data["azp"],
        name=data["name"],
        username=data["username"],
        email=data["email"],
        oid=data["oid"],
        roles=data["roles"],
    )

    assert _user.sub == data["sub"]
    assert _user.name == data["name"]
    assert _user.username == data["username"]
    assert _user.email == data["email"]
    assert _user.oid == data["oid"]
    assert _user.roles == data["roles"]


def test_has_role():
    assert user_obj.has_role("Study.Write") is True
    assert (
        dummy_user(roles={"Study.Read", "Library.Read"}).has_role("Study.Write")
        is False
    )


@pytest.mark.parametrize(
    "roles, has_all, expected_rs",
    [
        pytest.param(
            ("Study.Read", "Study.Write", "Library.Write", "Library.Read"), True, True
        ),
        pytest.param(("Study.Read", "Study.Write"), True, True),
        pytest.param(
            ("Study.Read", "Study.Write", "Library.Write", "Library.Read"), False, True
        ),
        pytest.param(("Study.Read", "Study.Write"), False, True),
    ],
)
def test_has_roles(roles, has_all, expected_rs):
    assert user_obj.has_roles(*roles, has_all=has_all) is expected_rs


def test_has_roles_negative():
    _user = dummy_user(roles={"Study.Read", "Study.Write", "Library.Write"})
    assert _user.has_roles("Library.Read", has_all=True) is False
    assert (
        _user.has_roles(
            "Study.Read", "Study.Write", "Library.Write", "Library.Read", has_all=True
        )
        is False
    )

    assert _user.has_roles("Library.Read", has_all=False) is False
    assert (
        _user.has_roles(
            "Study.Read", "Study.Write", "Library.Write", "Library.Read", has_all=False
        )
        is True
    )


def test_hasnt_role():
    assert user_obj.hasnt_role("Study.Read") is False
    assert (
        dummy_user({"Study.Read", "Study.Write", "Library.Write"}).hasnt_role(
            "Library.Read"
        )
        is True
    )


@pytest.mark.parametrize(
    "roles, hasnt_any, expected_rs",
    [
        pytest.param(
            ("Study.Read", "Study.Write", "Library.Write", "Library.Read"), True, False
        ),
        pytest.param(("Study.Read", "Study.Write"), True, False),
        pytest.param(
            ("Study.Read", "Study.Write", "Library.Write", "Library.Read"), False, False
        ),
        pytest.param(("Study.Read", "Study.Write"), False, False),
    ],
)
def test_hasnt_roles(roles, hasnt_any, expected_rs):
    assert user_obj.hasnt_roles(*roles, hasnt_any=hasnt_any) is expected_rs


def test_hasnt_roles_negative():
    _user = dummy_user({"Study.Read", "Study.Write", "Library.Write"})
    assert _user.hasnt_roles("Library.Read", hasnt_any=True) is True
    assert _user.hasnt_roles("Library.Read", "Study.Read", hasnt_any=True) is False
    assert (
        _user.hasnt_roles(
            "Study.Read", "Study.Write", "Library.Write", "Library.Read", hasnt_any=True
        )
        is False
    )

    assert _user.hasnt_roles("Library.Read", hasnt_any=False) is True
    assert _user.hasnt_roles("Library.Read", "Study.Read", hasnt_any=False) is True
    assert (
        _user.hasnt_roles(
            "Study.Read",
            "Study.Write",
            "Library.Write",
            "Library.Read",
            hasnt_any=False,
        )
        is True
    )


def test_has_only_role():
    assert dummy_user(roles={"Study.Read"}).has_only_role("Study.Read") is True
    assert user_obj.has_only_role("Study.Read") is False


@pytest.mark.parametrize(
    "roles, expected_rs",
    [
        pytest.param(
            (
                "Admin.Read",
                "Admin.Write",
                "Study.Read",
                "Study.Write",
                "Library.Write",
                "Library.Read",
            ),
            True,
        ),
        pytest.param(("Study.Read", "Study.Write"), False),
    ],
)
def test_has_only_roles(roles, expected_rs):
    assert user_obj.has_only_roles(*roles) is expected_rs


@pytest.mark.parametrize(
    "roles, has_all, expected_rs",
    [
        pytest.param(
            ("Study.Read", "Study.Write", "Library.Write", "Library.Read"), True, True
        ),
        pytest.param(("Study.Read", "Study.Write"), True, True),
    ],
)
def test_authorize(roles, has_all, expected_rs):
    assert user_obj.authorize(*roles, has_all=has_all) is expected_rs


def test_authorize_negative():
    _user = dummy_user({"Study.Read", "Study.Write"})
    assert (
        _user.hasnt_roles(
            "Study.Read",
            "Study.Write",
            "Library.Write",
            "Library.Read",
            hasnt_any=False,
        )
        is True
    )
    assert _user.hasnt_roles("Study.Read", "Library.Read", hasnt_any=False) is True

    with pytest.raises(ForbiddenException) as exc:
        _user.authorize("Library.Read", "Library.Write", has_all=True)
    assert (
        exc.value.msg
        == "Following roles are required: ['Library.Read', 'Library.Write']"
    )

    with pytest.raises(ForbiddenException) as exc:
        _user.authorize("Library.Read", "Library.Write", has_all=False)
    assert (
        exc.value.msg
        == "At least one of the following roles is required: ['Library.Read', 'Library.Write']"
    )


def test_access_token_claims_role_normalization():
    # Base claims required by JWTTokenClaims
    base_claims = {
        "iss": "https://keycloak.example.com",
        "sub": "user123",
        "aud": ["my-app"],
        "exp": 1999999999,
        "iat": 1555555555,
    }

    # Case 1: Simple/legacy flat roles array
    claims_flat = {**base_claims, "roles": ["legacy-role1", "legacy-role2"]}
    token_claims = AccessTokenClaims.model_validate(claims_flat)
    assert token_claims.roles == {"legacy-role1", "legacy-role2"}

    # Case 2: Standard Keycloak realm roles
    claims_realm = {
        **base_claims,
        "realm_access": {
            "roles": ["offline_access", "uma_authorization", "realm-admin"]
        }
    }
    token_claims = AccessTokenClaims.model_validate(claims_realm)
    assert token_claims.roles == {"offline_access", "uma_authorization", "realm-admin"}

    # Case 3: Standard Keycloak resource/client roles
    claims_resource = {
        **base_claims,
        "resource_access": {
            "account": {
                "roles": ["view-profile", "manage-account"]
            },
            "my-client": {
                "roles": ["client-admin"]
            }
        }
    }
    token_claims = AccessTokenClaims.model_validate(claims_resource)
    assert token_claims.roles == {"view-profile", "manage-account", "client-admin"}

    # Case 4: Mixture of flat, realm-level, and resource-level roles
    claims_mixed = {
        **base_claims,
        "roles": ["root-role"],
        "realm_access": {
            "roles": ["realm-role"]
        },
        "resource_access": {
            "client-a": {
                "roles": ["client-role"]
            }
        }
    }
    token_claims = AccessTokenClaims.model_validate(claims_mixed)
    assert token_claims.roles == {"root-role", "realm-role", "client-role"}

    # Case 5: Missing or empty roles -> falls back to empty collection safely
    claims_empty = {**base_claims}
    token_claims = AccessTokenClaims.model_validate(claims_empty)
    assert token_claims.roles == set()

    # Case 6: Malformed/unexpected structures -> should not crash and should fall back safely
    claims_malformed = {
        **base_claims,
        "roles": "not-a-list-but-a-string",
        "realm_access": "malformed-realm-access-string",
        "resource_access": ["malformed-resource-access-list"]
    }
    token_claims = AccessTokenClaims.model_validate(claims_malformed)
    assert token_claims.roles == {"not-a-list-but-a-string"}


