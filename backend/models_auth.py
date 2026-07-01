"""
Pydantic schemas for authentication & users.

EFUEL Engineering Hub is now a multi-user enterprise app with 5 roles:
    - super_admin: full system access, including user management, API
      integrations, and system settings.
    - admin: manage catalog data (brands/products/documents) and view logs;
      cannot manage other admins or system-level integration keys.
    - engineer: full access to AI Search, Compare, BOM Builder, Documents.
    - procurement: focused on BOM Builder, Compare & sourcing documents.
    - viewer: read-only access to research results, comparisons & documents.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal

Role = Literal['super_admin', 'admin', 'engineer', 'procurement', 'viewer']

# Roles allowed to access the Admin Panel (admin-gated routes).
ADMIN_ROLES = ('super_admin', 'admin')

ROLE_DEFINITIONS = [
    {
        'value': 'super_admin', 'label': 'Super Admin',
        'description': 'Full system access - user management, API integrations, system settings and all catalog data.',
    },
    {
        'value': 'admin', 'label': 'Admin',
        'description': 'Manage brands, categories, products and documents. View logs. Cannot manage other admins or integration keys.',
    },
    {
        'value': 'engineer', 'label': 'Engineer',
        'description': 'Full access to AI Search, Compare, BOM Builder, Component Library and Document Library.',
    },
    {
        'value': 'procurement', 'label': 'Procurement',
        'description': 'Focused on BOM Builder, Compare and sourcing documents for purchasing decisions.',
    },
    {
        'value': 'viewer', 'label': 'Viewer',
        'description': 'Read-only access to research results, comparisons and documents.',
    },
]


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    role: Role = 'engineer'


class UserAdminUpdate(BaseModel):
    """Admin-only partial update of another user's profile."""
    name: Optional[str] = Field(None, min_length=2, max_length=80)
    email: Optional[EmailStr] = None
    role: Optional[Role] = None
    is_active: Optional[bool] = None


class PasswordReset(BaseModel):
    new_password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: str
    name: str
    email: str
    role: Role
    is_active: bool = True
    created_at: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    user: UserPublic
