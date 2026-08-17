# ============================================================
# ROLE-BASED DOCUMENT ACCESS CONTROL
# ============================================================


# ============================================================
# DOCUMENT PERMISSIONS
# ============================================================

DOCUMENT_PERMISSIONS = {

    # --------------------------------------------------------
    # General employee documents
    # --------------------------------------------------------

    "employee_handbook.pdf": {
        "classification": "internal",
        "allowed_roles": [
            "employee",
            "manager",
            "admin"
        ]
    },

    "it_security_policy.pdf": {
        "classification": "internal",
        "allowed_roles": [
            "employee",
            "manager",
            "admin"
        ]
    },

    "enterprise_remote_work_policy.pdf": {
        "classification": "internal",
        "allowed_roles": [
            "employee",
            "manager",
            "admin"
        ]
    },

    "enterprise_information_security_training.pdf": {
        "classification": "internal",
        "allowed_roles": [
            "employee",
            "manager",
            "admin"
        ]
    },

    # --------------------------------------------------------
    # Restricted HR document
    # --------------------------------------------------------

    "hr_confidential.pdf": {
        "classification": "restricted",
        "allowed_roles": [
            "hr",
            "admin"
        ]
    }
}


# ============================================================
# REGISTER NEW DOCUMENT
# ============================================================

def register_document(
    filename,
    classification="internal",
    allowed_roles=None
):
    """
    Register a newly uploaded document.

    By default, uploaded documents are treated as
    internal documents accessible to employee,
    manager and admin.
    """

    if allowed_roles is None:

        allowed_roles = [
            "employee",
            "manager",
            "admin"
        ]

    filename = (
        filename
        .replace("\\", "/")
        .split("/")[-1]
        .lower()
        .strip()
    )

    DOCUMENT_PERMISSIONS[filename] = {
        "classification": classification,
        "allowed_roles": allowed_roles
    }

    print(
        f"Document registered: {filename}"
    )

    print(
        f"Classification: {classification}"
    )

    print(
        f"Allowed roles: {allowed_roles}"
    )


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
    # Extract filename
    # --------------------------------------------------------

    document_name = (
        document_source
        .replace("\\", "/")
        .split("/")[-1]
        .lower()
        .strip()
    )

    # --------------------------------------------------------
    # Get document permission
    # --------------------------------------------------------

    permission = DOCUMENT_PERMISSIONS.get(
        document_name
    )

    # --------------------------------------------------------
    # Unknown document = DENY
    # --------------------------------------------------------

    if permission is None:

        return False

    # --------------------------------------------------------
    # Check allowed roles
    # --------------------------------------------------------

    allowed_roles = permission[
        "allowed_roles"
    ]

    return user_role in allowed_roles


# ============================================================
# FILTER AUTHORIZED RESULTS
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
# GET DOCUMENTS FOR ROLE
# ============================================================

def get_documents_for_role(
    user_role
):
    """
    Return all documents that the given role
    is authorized to access.
    """

    user_role = (
        user_role
        .lower()
        .strip()
    )

    documents = []

    for filename, permission in (
        DOCUMENT_PERMISSIONS.items()
    ):

        allowed_roles = permission[
            "allowed_roles"
        ]

        if user_role in allowed_roles:

            documents.append({

                "filename": filename,

                "classification": permission[
                    "classification"
                ],

                "access": "ALLOWED"

            })

    return documents


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("DOCUMENT REGISTRY TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # Employee
    # --------------------------------------------------------

    print("\nEmployee documents:")

    print(
        get_documents_for_role(
            "employee"
        )
    )

    # --------------------------------------------------------
    # HR
    # --------------------------------------------------------

    print("\nHR documents:")

    print(
        get_documents_for_role(
            "hr"
        )
    )

    # --------------------------------------------------------
    # Admin
    # --------------------------------------------------------

    print("\nAdmin documents:")

    print(
        get_documents_for_role(
            "admin"
        )
    )

    # --------------------------------------------------------
    # Authorization tests
    # --------------------------------------------------------

    test_cases = [

        (
            "employee",
            "employee_handbook.pdf"
        ),

        (
            "employee",
            "hr_confidential.pdf"
        ),

        (
            "hr",
            "hr_confidential.pdf"
        ),

        (
            "admin",
            "hr_confidential.pdf"
        )

    ]

    print("\n" + "=" * 60)
    print("AUTHORIZATION TEST")
    print("=" * 60)

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
            "Access:",
            "ALLOWED"
            if result
            else "DENIED"
        )