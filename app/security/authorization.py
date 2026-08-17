# ============================================================
# ROLE-BASED ACCESS CONTROL
# ============================================================

DOCUMENT_PERMISSIONS = {

    # --------------------------------------------------------
    # General employee documents
    # --------------------------------------------------------

    "employee_handbook.pdf": [
        "employee",
        "manager",
        "admin"
    ],

    "it_security_policy.pdf": [
        "employee",
        "manager",
        "admin"
    ],

    "enterprise_remote_work_policy.pdf": [
        "employee",
        "manager",
        "admin"
    ],

    "enterprise_information_security_training.pdf": [
        "employee",
        "manager",
        "admin"
    ],

    # --------------------------------------------------------
    # Restricted HR document
    # --------------------------------------------------------

    "hr_confidential.pdf": [
        "hr",
        "admin"
    ]
}


# ============================================================
# CHECK DOCUMENT ACCESS
# ============================================================

def is_authorized(
    user_role,
    document_source
):
    """
    Check whether a user role can access
    a particular document.

    Args:
        user_role: Role of the current user.
        document_source: Document filename/path.

    Returns:
        True if authorized, otherwise False.
    """

    # --------------------------------------------------------
    # Normalize role
    # --------------------------------------------------------

    user_role = (
        user_role
        .lower()
        .strip()
    )

    # --------------------------------------------------------
    # Extract only filename from source path
    # --------------------------------------------------------

    document_name = (
        document_source
        .replace("\\", "/")
        .split("/")[-1]
        .lower()
    )

    # --------------------------------------------------------
    # Get allowed roles
    # --------------------------------------------------------

    allowed_roles = DOCUMENT_PERMISSIONS.get(
        document_name
    )

    # --------------------------------------------------------
    # Unknown document = DENY
    # --------------------------------------------------------

    if allowed_roles is None:

        return False

    # --------------------------------------------------------
    # Check role permission
    # --------------------------------------------------------

    return user_role in allowed_roles


# ============================================================
# FILTER AUTHORIZED DOCUMENTS
# ============================================================

def filter_authorized_results(
    results,
    user_role
):
    """
    Remove documents that the current user
    is not authorized to access.
    """

    authorized_results = []

    for result in results:

        document = result["document"]

        source = document.metadata.get(
            "source",
            ""
        )

        if is_authorized(
            user_role,
            source
        ):

            authorized_results.append(
                result
            )

    return authorized_results


# ============================================================
# AUTHORIZATION TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("AUTHORIZATION TEST")
    print("=" * 60)

    test_cases = [

        # ----------------------------------------------------
        # Employee access
        # ----------------------------------------------------

        (
            "employee",
            "employee_handbook.pdf"
        ),

        (
            "employee",
            "it_security_policy.pdf"
        ),

        # ----------------------------------------------------
        # HR access
        # ----------------------------------------------------

        (
            "hr",
            "employee_handbook.pdf"
        ),

        (
            "hr",
            "hr_confidential.pdf"
        ),

        # ----------------------------------------------------
        # Admin access
        # ----------------------------------------------------

        (
            "admin",
            "it_security_policy.pdf"
        ),

        (
            "admin",
            "hr_confidential.pdf"
        ),

        # ----------------------------------------------------
        # Employee must NOT access HR confidential document
        # ----------------------------------------------------

        (
            "employee",
            "hr_confidential.pdf"
        )
    ]

    for role, document in test_cases:

        result = is_authorized(
            role,
            document
        )

        print(
            f"\nRole: {role}"
        )

        print(
            f"Document: {document}"
        )

        print(
            f"Access: "
            f"{'ALLOWED' if result else 'DENIED'}"
        )