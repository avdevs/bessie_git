# Demote User Functionality - Implementation Summary

## What was implemented:

### 1. Backend Views (in `bessie/views/accounts.py`):

- **`get_user_companies_for_demotion(request)`**: Returns companies that a user is currently admin for
- **`demote_user_from_admin(request)`**: Removes user from admin role for selected companies, and demotes them completely if no companies remain

### 2. URL Patterns (in `bessie/urls.py`):

- `/bessie/get-user-companies-for-demotion/` - GET endpoint to fetch user's current admin companies
- `/bessie/demote-user-from-admin/` - POST endpoint to process demotion

### 3. Frontend Template Updates (in `bessie/templates/bessie/all_system_users.html`):

- Updated "Demote user" button to call `openDemoteModal()` instead of `openPromoteModal()`
- Added new demote modal with separate form and styling
- Updated JavaScript to handle both promote and demote workflows

## How it works:

1. **For Bessie Admins**: The "Demote user" button opens a modal showing all companies the user currently has admin access to
2. **Company Selection**: All companies are pre-checked, but users can uncheck specific ones to keep admin access for those companies
3. **Demotion Logic**:
   - If user still has admin access to other companies after demotion, they remain as `COMPANY_ADMIN` with `bessie_admin=True`
   - If user has no remaining company admin roles, they are demoted to `EMPLOYEE` with `bessie_admin=False`

## Security:

- Only `STAFF` users can demote other users
- Proper CSRF protection
- Form validation and error handling
- User authentication checks

## Testing:

To test the functionality:

1. Log in as a STAFF user
2. Navigate to the system users page
3. Find a user who is currently a Bessie Admin (has `bessie_admin=True`)
4. Click "Demote user" button
5. Select companies to remove admin access from
6. Submit the form
7. Verify the user's status is updated correctly
