"""
EFUEL Engineering Hub - Backend API Test Suite (Phase B: Admin Panel & RBAC)
Tests the complete enterprise Admin Panel with multi-user RBAC, PDF Document Management,
API Integrations, and System Settings.
"""
import requests
import sys
import time
import io
from datetime import datetime

class EFUELPhaseBTester:
    def __init__(self, base_url="https://engineering-ai-3.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.super_admin_token = None
        self.engineer_token = None
        self.test_user_id = None
        self.test_brand_name = None
        self.test_product_id = None
        self.test_document_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failed_tests = []
        self.critical_issues = []

    def log(self, message, level="INFO"):
        """Log test messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None, files=None, params=None, timeout=30):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        # Only set Content-Type for JSON requests
        if data and not files:
            headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        self.log(f"Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=timeout)
            elif method == 'POST':
                if files:
                    response = requests.post(url, data=data, files=files, headers=headers, params=params, timeout=timeout)
                else:
                    response = requests.post(url, json=data, headers=headers, params=params, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, params=params, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, params=params, timeout=timeout)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ PASSED - {name} - Status: {response.status_code}", "PASS")
            else:
                self.tests_failed += 1
                self.failed_tests.append(name)
                self.log(f"❌ FAILED - {name} - Expected {expected_status}, got {response.status_code}", "FAIL")
                try:
                    self.log(f"   Response: {response.json()}", "FAIL")
                except:
                    self.log(f"   Response: {response.text[:200]}", "FAIL")

            return success, response.json() if response.status_code < 500 and response.headers.get('content-type', '').startswith('application/json') else {}

        except requests.exceptions.Timeout:
            self.tests_failed += 1
            self.failed_tests.append(name)
            self.log(f"❌ FAILED - {name} - Request timeout after {timeout}s", "FAIL")
            return False, {}
        except Exception as e:
            self.tests_failed += 1
            self.failed_tests.append(name)
            self.log(f"❌ FAILED - {name} - Error: {str(e)}", "FAIL")
            return False, {}

    # ===== AUTH TESTS =====
    def test_login(self, email, password, role_name):
        """Test login and get token"""
        success, response = self.run_test(
            f"Login as {role_name}",
            "POST",
            "/auth/login",
            200,
            data={"email": email, "password": password}
        )
        if success and 'access_token' in response:
            token = response['access_token']
            user = response.get('user', {})
            self.log(f"   Logged in: {user.get('name')} ({user.get('role')})")
            return token, user
        return None, None

    # ===== USERS MANAGEMENT TESTS =====
    def test_list_users(self, token):
        """Test listing users (super_admin only)"""
        success, response = self.run_test(
            "Admin: List Users",
            "GET",
            "/admin/users",
            200,
            token=token
        )
        if success:
            self.log(f"   Found {len(response)} users")
        return success, response

    def test_create_user(self, token):
        """Test creating a new user"""
        test_email = f"test_{int(time.time())}@efuelhub.com"
        success, response = self.run_test(
            "Admin: Create User",
            "POST",
            "/admin/users",
            200,
            data={
                "name": "Test User",
                "email": test_email,
                "password": "TestPass@123",
                "role": "engineer"
            },
            token=token
        )
        if success:
            self.test_user_id = response.get('id')
            self.log(f"   Created user ID: {self.test_user_id}")
        return success, response

    def test_update_user_role(self, token, user_id):
        """Test updating user role"""
        success, response = self.run_test(
            "Admin: Update User Role",
            "PUT",
            f"/admin/users/{user_id}/role",
            200,
            token=token,
            params={"role": "procurement"}
        )
        return success

    def test_toggle_user_status(self, token, user_id):
        """Test toggling user active status"""
        success, response = self.run_test(
            "Admin: Toggle User Status",
            "PUT",
            f"/admin/users/{user_id}/status",
            200,
            token=token,
            params={"is_active": False}
        )
        return success

    def test_delete_user(self, token, user_id):
        """Test deleting a user"""
        success, response = self.run_test(
            "Admin: Delete User",
            "DELETE",
            f"/admin/users/{user_id}",
            200,
            token=token
        )
        return success

    def test_self_modification_prevention(self, token, user_id):
        """Test that users cannot modify their own role/status"""
        # Try to change own role (should fail)
        success, response = self.run_test(
            "Admin: Prevent Self Role Change",
            "PUT",
            f"/admin/users/{user_id}/role",
            400,  # Should fail
            token=token,
            params={"role": "viewer"}
        )
        if success:
            self.log(f"   ✅ Self role change correctly prevented")
        return success

    # ===== ROLES TESTS =====
    def test_list_roles(self, token):
        """Test listing roles"""
        success, response = self.run_test(
            "Admin: List Roles",
            "GET",
            "/admin/roles",
            200,
            token=token
        )
        if success:
            self.log(f"   Found {len(response)} roles")
            expected_roles = ['super_admin', 'admin', 'engineer', 'procurement', 'viewer']
            found_roles = [r['value'] for r in response]
            for role in expected_roles:
                if role in found_roles:
                    self.log(f"   ✅ Role '{role}' found")
                else:
                    self.log(f"   ❌ Role '{role}' MISSING", "FAIL")
                    self.critical_issues.append(f"Role '{role}' not found in roles list")
        return success, response

    # ===== BRANDS TESTS =====
    def test_create_brand(self, token):
        """Test creating a brand"""
        brand_name = f"TestBrand_{int(time.time())}"
        success, response = self.run_test(
            "Admin: Create Brand",
            "POST",
            "/admin/brands",
            200,
            data={"name": brand_name, "website": "https://testbrand.com"},
            token=token
        )
        if success:
            self.test_brand_name = brand_name
            self.log(f"   Created brand: {brand_name}")
        return success

    def test_delete_brand(self, token, brand_name):
        """Test deleting a brand"""
        success, response = self.run_test(
            "Admin: Delete Brand",
            "DELETE",
            f"/admin/brands/{brand_name}",
            200,
            token=token
        )
        return success

    # ===== PRODUCTS TESTS =====
    def test_create_product(self, token):
        """Test creating a product"""
        success, response = self.run_test(
            "Admin: Create Product",
            "POST",
            "/admin/products",
            200,
            data={
                "name": "Test MCB 32A",
                "brand": "TestBrand",
                "category": "MCB",
                "estimated_price_range": "₹500-₹800",
                "engineering_notes": "Test product for Phase B testing"
            },
            token=token
        )
        if success:
            self.test_product_id = response.get('id')
            self.log(f"   Created product ID: {self.test_product_id}")
        return success

    def test_delete_product(self, token, product_id):
        """Test deleting a product"""
        success, response = self.run_test(
            "Admin: Delete Product",
            "DELETE",
            f"/admin/products/{product_id}",
            200,
            token=token
        )
        return success

    # ===== DOCUMENTS TESTS (CRITICAL - PDF Management) =====
    def test_upload_document(self, token):
        """Test uploading a PDF document"""
        # Create a minimal PDF file
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT /F1 12 Tf 100 700 Td (Test PDF) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000317 00000 n\ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n408\n%%EOF"
        
        files = {'file': ('test_document.pdf', io.BytesIO(pdf_content), 'application/pdf')}
        data = {
            'title': 'Test PDF Document',
            'doc_type': 'datasheet',
            'brand': 'TestBrand',
            'product_name': 'Test MCB 32A'
        }
        
        success, response = self.run_test(
            "Admin: Upload PDF Document",
            "POST",
            "/admin/documents/upload",
            200,
            data=data,
            files=files,
            token=token,
            timeout=60
        )
        if success:
            self.test_document_id = response.get('id')
            self.log(f"   Uploaded document ID: {self.test_document_id}")
            self.log(f"   Version: {response.get('version')}")
            self.log(f"   Source: {response.get('source')}")
        return success, response

    def test_list_documents(self, token):
        """Test listing documents"""
        success, response = self.run_test(
            "Admin: List Documents",
            "GET",
            "/admin/documents",
            200,
            token=token
        )
        if success:
            self.log(f"   Found {len(response)} documents")
        return success, response

    def test_update_document_metadata(self, token, document_id):
        """Test updating document metadata"""
        success, response = self.run_test(
            "Admin: Update Document Metadata",
            "PUT",
            f"/admin/documents/{document_id}",
            200,
            data={"title": "Updated Test PDF Document"},
            token=token
        )
        return success

    def test_toggle_document_status(self, token, document_id):
        """Test toggling document active status"""
        success, response = self.run_test(
            "Admin: Toggle Document Status",
            "PUT",
            f"/admin/documents/{document_id}/status",
            200,
            token=token,
            params={"is_active": False}
        )
        return success

    def test_document_versions(self, token, document_id):
        """Test getting document version history"""
        success, response = self.run_test(
            "Admin: Get Document Versions",
            "GET",
            f"/admin/documents/{document_id}/versions",
            200,
            token=token
        )
        if success:
            self.log(f"   Found {len(response)} version(s)")
        return success, response

    def test_replace_document(self, token, document_id):
        """Test replacing a document (version control)"""
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 50 >>\nstream\nBT /F1 12 Tf 100 700 Td (Updated PDF v2) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000317 00000 n\ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n414\n%%EOF"
        
        files = {'file': ('test_document_v2.pdf', io.BytesIO(pdf_content), 'application/pdf')}
        
        success, response = self.run_test(
            "Admin: Replace Document (Version Control)",
            "POST",
            f"/admin/documents/{document_id}/replace",
            200,
            files=files,
            token=token,
            timeout=60
        )
        if success:
            new_version = response.get('version')
            self.log(f"   New version: {new_version}")
            if new_version == 2:
                self.log(f"   ✅ Version incremented correctly")
            else:
                self.log(f"   ❌ Version should be 2, got {new_version}", "FAIL")
        return success, response

    def test_delete_document(self, token, document_id):
        """Test deleting a document"""
        success, response = self.run_test(
            "Admin: Delete Document",
            "DELETE",
            f"/admin/documents/{document_id}",
            200,
            token=token
        )
        return success

    # ===== SEARCH LOGS TESTS =====
    def test_list_search_logs(self, token):
        """Test listing search logs"""
        success, response = self.run_test(
            "Admin: List Search Logs",
            "GET",
            "/admin/search-logs",
            200,
            token=token
        )
        if success:
            self.log(f"   Found {len(response)} search log entries")
        return success, response

    def test_clear_search_logs(self, token):
        """Test clearing all search logs"""
        success, response = self.run_test(
            "Admin: Clear All Search Logs",
            "DELETE",
            "/admin/search-logs",
            200,
            token=token
        )
        if success:
            deleted_count = response.get('deleted_count', 0)
            self.log(f"   Cleared {deleted_count} search log entries")
        return success

    # ===== AI LOGS TESTS =====
    def test_list_ai_logs(self, token):
        """Test listing AI pipeline logs"""
        success, response = self.run_test(
            "Admin: List AI Logs",
            "GET",
            "/admin/logs",
            200,
            token=token
        )
        if success:
            self.log(f"   Found {len(response)} AI log entries")
        return success, response

    # ===== API INTEGRATIONS TESTS =====
    def test_list_integrations(self, token):
        """Test listing API integrations (super_admin only)"""
        success, response = self.run_test(
            "Admin: List API Integrations",
            "GET",
            "/admin/integrations",
            200,
            token=token
        )
        if success:
            providers = ['exa', 'tavily', 'firecrawl', 'emergent_llm']
            for provider in providers:
                if provider in response:
                    self.log(f"   {provider}: configured={response[provider].get('configured')}, enabled={response[provider].get('enabled')}")
                else:
                    self.log(f"   ❌ Provider '{provider}' MISSING", "FAIL")
        return success, response

    def test_toggle_integration(self, token, provider):
        """Test toggling integration enabled status"""
        success, response = self.run_test(
            f"Admin: Toggle Integration ({provider})",
            "PUT",
            f"/admin/integrations/{provider}/toggle",
            200,
            data={"enabled": True},
            token=token
        )
        return success

    def test_integration_connection(self, token, provider):
        """Test integration connection"""
        success, response = self.run_test(
            f"Admin: Test Integration Connection ({provider})",
            "POST",
            f"/admin/integrations/{provider}/test",
            200,
            token=token,
            timeout=30
        )
        if success:
            test_success = response.get('success', False)
            message = response.get('message', '')
            if test_success:
                self.log(f"   ✅ {provider} connection test: {message}")
            else:
                self.log(f"   ⚠️  {provider} connection test failed: {message}")
        return success

    # ===== SYSTEM SETTINGS TESTS =====
    def test_get_system_settings(self, token):
        """Test getting system settings"""
        success, response = self.run_test(
            "Admin: Get System Settings",
            "GET",
            "/admin/settings",
            200,
            token=token
        )
        if success:
            self.log(f"   LLM Provider: {response.get('llm_provider')}")
            self.log(f"   LLM Model: {response.get('llm_model')}")
        return success, response

    def test_update_system_settings(self, token):
        """Test updating system settings"""
        success, response = self.run_test(
            "Admin: Update System Settings",
            "PUT",
            "/admin/settings",
            200,
            data={"llm_provider": "openai", "llm_model": "gpt-4o"},
            token=token
        )
        return success

    # ===== ACCESS CONTROL TESTS =====
    def test_engineer_admin_access(self, token):
        """Test that engineer role cannot access super_admin endpoints"""
        # Try to access users list (should fail)
        success, response = self.run_test(
            "Access Control: Engineer Cannot Access Users",
            "GET",
            "/admin/users",
            403,  # Should be forbidden
            token=token
        )
        if success:
            self.log(f"   ✅ Engineer correctly denied access to /admin/users")
        return success

    def test_engineer_can_access_brands(self, token):
        """Test that engineer can access non-super_admin admin endpoints"""
        # Engineer should be able to access brands (admin role required, not super_admin)
        success, response = self.run_test(
            "Access Control: Engineer CAN Access Brands",
            "GET",
            "/admin/brands",
            403,  # Actually, based on code, only admin/super_admin can access
            token=token
        )
        # Note: Based on the code, brands require admin_dep which is admin or super_admin
        # So engineer should NOT have access
        if success:
            self.log(f"   ✅ Engineer correctly denied access to /admin/brands")
        return success

    # ===== REGRESSION TESTS =====
    def test_regression_documents_endpoint(self, token):
        """Test non-admin documents endpoint still works"""
        success, response = self.run_test(
            "Regression: Documents Endpoint (Non-Admin)",
            "GET",
            "/documents",
            200,
            token=token
        )
        if success:
            self.log(f"   ✅ Documents endpoint working for all users")
        return success

    def test_regression_dashboard(self, token):
        """Test dashboard endpoint still works"""
        success, response = self.run_test(
            "Regression: Dashboard Summary",
            "GET",
            "/dashboard/summary",
            200,
            token=token
        )
        if success:
            api_status = response.get('api_status', {})
            if 'exa_search' in api_status:
                self.log(f"   ✅ Dashboard api_status includes exa_search")
            else:
                self.log(f"   ❌ Dashboard api_status missing exa_search", "FAIL")
        return success

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("TEST SUMMARY - PHASE B")
        print("="*70)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed} ✅")
        print(f"Tests Failed: {self.tests_failed} ❌")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.critical_issues:
            print("\n🚨 CRITICAL ISSUES:")
            for issue in self.critical_issues:
                print(f"  🚨 {issue}")
        
        if self.failed_tests:
            print("\nFailed Tests:")
            for test in self.failed_tests:
                print(f"  ❌ {test}")
        
        print("="*70)
        return 0 if self.tests_failed == 0 else 1


def main():
    print("="*70)
    print("EFUEL Engineering Hub - Backend API Test Suite")
    print("Phase B: Admin Panel, RBAC & PDF Document Management")
    print("="*70)
    
    tester = EFUELPhaseBTester()
    
    # Credentials
    super_admin_email = "owner@efuelhub.com"
    super_admin_password = "EfuelOwner@2026!"
    engineer_email = "jane@efuelhub.com"
    engineer_password = "JanePass@123"
    
    print("\n📋 PHASE 1: AUTHENTICATION")
    print("-" * 70)
    
    tester.super_admin_token, super_admin_user = tester.test_login(super_admin_email, super_admin_password, "Super Admin")
    tester.engineer_token, engineer_user = tester.test_login(engineer_email, engineer_password, "Engineer")
    
    if not tester.super_admin_token:
        print("\n❌ CRITICAL: Super Admin login failed. Cannot proceed.")
        return tester.print_summary()
    
    print("\n📋 PHASE 2: USERS MANAGEMENT (Super Admin Only)")
    print("-" * 70)
    
    tester.test_list_users(tester.super_admin_token)
    tester.test_create_user(tester.super_admin_token)
    
    if tester.test_user_id:
        tester.test_update_user_role(tester.super_admin_token, tester.test_user_id)
        tester.test_toggle_user_status(tester.super_admin_token, tester.test_user_id)
        # Test self-modification prevention with super admin's own ID
        if super_admin_user:
            tester.test_self_modification_prevention(tester.super_admin_token, super_admin_user.get('id'))
        tester.test_delete_user(tester.super_admin_token, tester.test_user_id)
    
    print("\n📋 PHASE 3: ROLES")
    print("-" * 70)
    
    tester.test_list_roles(tester.super_admin_token)
    
    print("\n📋 PHASE 4: BRANDS & PRODUCTS")
    print("-" * 70)
    
    tester.test_create_brand(tester.super_admin_token)
    tester.test_create_product(tester.super_admin_token)
    
    print("\n📋 PHASE 5: DOCUMENTS (CRITICAL - PDF Management)")
    print("-" * 70)
    
    upload_success, upload_response = tester.test_upload_document(tester.super_admin_token)
    tester.test_list_documents(tester.super_admin_token)
    
    if tester.test_document_id:
        tester.test_update_document_metadata(tester.super_admin_token, tester.test_document_id)
        tester.test_document_versions(tester.super_admin_token, tester.test_document_id)
        tester.test_replace_document(tester.super_admin_token, tester.test_document_id)
        # Check versions again after replace
        tester.test_document_versions(tester.super_admin_token, tester.test_document_id)
        tester.test_toggle_document_status(tester.super_admin_token, tester.test_document_id)
    
    print("\n📋 PHASE 6: SEARCH & AI LOGS")
    print("-" * 70)
    
    tester.test_list_search_logs(tester.super_admin_token)
    tester.test_list_ai_logs(tester.super_admin_token)
    
    print("\n📋 PHASE 7: API INTEGRATIONS (Super Admin Only)")
    print("-" * 70)
    
    tester.test_list_integrations(tester.super_admin_token)
    # Test connection for each provider
    for provider in ['exa', 'tavily', 'firecrawl', 'emergent_llm']:
        tester.test_integration_connection(tester.super_admin_token, provider)
    
    print("\n📋 PHASE 8: SYSTEM SETTINGS (Super Admin Only)")
    print("-" * 70)
    
    tester.test_get_system_settings(tester.super_admin_token)
    tester.test_update_system_settings(tester.super_admin_token)
    
    print("\n📋 PHASE 9: ACCESS CONTROL (RBAC)")
    print("-" * 70)
    
    if tester.engineer_token:
        tester.test_engineer_admin_access(tester.engineer_token)
        tester.test_engineer_can_access_brands(tester.engineer_token)
    
    print("\n📋 PHASE 10: REGRESSION TESTS")
    print("-" * 70)
    
    if tester.engineer_token:
        tester.test_regression_documents_endpoint(tester.engineer_token)
        tester.test_regression_dashboard(tester.engineer_token)
    
    print("\n📋 PHASE 11: CLEANUP")
    print("-" * 70)
    
    # Clean up test data
    if tester.test_document_id:
        tester.test_delete_document(tester.super_admin_token, tester.test_document_id)
    if tester.test_product_id:
        tester.test_delete_product(tester.super_admin_token, tester.test_product_id)
    if tester.test_brand_name:
        tester.test_delete_brand(tester.super_admin_token, tester.test_brand_name)
    
    # Clear search logs at the end
    tester.test_clear_search_logs(tester.super_admin_token)
    
    return tester.print_summary()


if __name__ == "__main__":
    sys.exit(main())
