"""
EFUEL Engineering Hub - Backend API Test Suite
Tests all API endpoints with proper authentication and role-based access control.
"""
import requests
import sys
import time
from datetime import datetime

class EFUELAPITester:
    def __init__(self, base_url="https://engineering-ai-3.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.admin_token = None
        self.engineer_token = None
        self.viewer_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failed_tests = []

    def log(self, message, level="INFO"):
        """Log test messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None, timeout=40):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        self.tests_run += 1
        self.log(f"Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout)

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

            return success, response.json() if response.status_code < 500 else {}

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
    def test_health(self):
        """Test health endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "/health",
            200
        )
        if success:
            self.log(f"   Tavily: {response.get('tavily_configured')}, Firecrawl: {response.get('firecrawl_configured')}, LLM: {response.get('llm_configured')}")
        return success

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
            return token
        return None

    def test_register(self):
        """Test user registration"""
        timestamp = datetime.now().strftime("%H%M%S")
        success, response = self.run_test(
            "Register New User",
            "POST",
            "/auth/register",
            200,
            data={
                "name": f"Test User {timestamp}",
                "email": f"test_{timestamp}@efuel.com",
                "password": "TestPass123!",
                "role": "engineer"
            }
        )
        return success

    def test_me(self, token, expected_role):
        """Test get current user"""
        success, response = self.run_test(
            f"Get Current User ({expected_role})",
            "GET",
            "/auth/me",
            200,
            token=token
        )
        if success:
            self.log(f"   User: {response.get('name')} - Role: {response.get('role')}")
        return success

    # ===== RESEARCH TESTS =====
    def test_ai_search(self, token, query="MCB"):
        """Test AI search - takes 15-25 seconds"""
        self.log(f"Starting AI Search for '{query}' (this will take 20-30 seconds)...")
        success, response = self.run_test(
            f"AI Search: {query}",
            "POST",
            "/research",
            200,
            data={"query": query, "force_refresh": False},
            token=token,
            timeout=45  # Generous timeout for AI processing
        )
        if success:
            self.log(f"   Category: {response.get('category')}, Products: {len(response.get('products', []))}")
            return response.get('id')
        return None

    def test_get_research_by_id(self, token, result_id):
        """Test get research result by ID"""
        success, response = self.run_test(
            "Get Research by ID",
            "GET",
            f"/research/{result_id}",
            200,
            token=token
        )
        return success

    def test_search_history(self, token):
        """Test get search history"""
        success, response = self.run_test(
            "Get Search History",
            "GET",
            "/research/history",
            200,
            token=token
        )
        if success:
            self.log(f"   Search history count: {len(response)}")
        return success

    def test_list_cached_research(self, token):
        """Test list cached research results"""
        success, response = self.run_test(
            "List Cached Research",
            "GET",
            "/research?limit=10",
            200,
            token=token
        )
        if success:
            self.log(f"   Cached results: {len(response)}")
        return success

    # ===== COMPARE TESTS =====
    def test_compare_products(self, token):
        """Test product comparison"""
        self.log("Starting Product Comparison (this will take 20-30 seconds)...")
        # Mock product data for comparison
        products = [
            {"name": "Schneider MCB 32A", "brand": "Schneider", "category": "MCB"},
            {"name": "Siemens MCB 32A", "brand": "Siemens", "category": "MCB"}
        ]
        success, response = self.run_test(
            "Compare Products",
            "POST",
            "/compare",
            200,
            data={"products": products, "query_category": "MCB"},
            token=token,
            timeout=45
        )
        if success:
            self.log(f"   Comparison ID: {response.get('id')}")
        return success

    def test_compare_history(self, token):
        """Test get compare history"""
        success, response = self.run_test(
            "Get Compare History",
            "GET",
            "/compare/history",
            200,
            token=token
        )
        if success:
            self.log(f"   Compare history count: {len(response)}")
        return success

    # ===== CHAT TESTS =====
    def test_chat(self, token):
        """Test AI chat assistant"""
        self.log("Starting AI Chat (this will take 10-20 seconds)...")
        success, response = self.run_test(
            "AI Chat",
            "POST",
            "/chat",
            200,
            data={"message": "What is an MCB?", "session_id": None},
            token=token,
            timeout=30
        )
        if success:
            self.log(f"   Session ID: {response.get('session_id')}")
            self.log(f"   Reply preview: {response.get('reply', '')[:100]}...")
            return response.get('session_id')
        return None

    def test_chat_sessions(self, token):
        """Test list chat sessions"""
        success, response = self.run_test(
            "List Chat Sessions",
            "GET",
            "/chat/sessions",
            200,
            token=token
        )
        if success:
            self.log(f"   Chat sessions count: {len(response)}")
        return success

    def test_get_chat_session(self, token, session_id):
        """Test get specific chat session"""
        success, response = self.run_test(
            "Get Chat Session",
            "GET",
            f"/chat/sessions/{session_id}",
            200,
            token=token
        )
        return success

    # ===== BOM TESTS =====
    def test_generate_bom(self, token):
        """Test BOM generation"""
        self.log("Starting BOM Generation (this will take 20-30 seconds)...")
        success, response = self.run_test(
            "Generate BOM",
            "POST",
            "/bom/generate",
            200,
            data={
                "project_name": "Test 30kW EV Charger",
                "requirement": "30kW EV Charger with MCB, MCCB, SPD, Energy Meter"
            },
            token=token,
            timeout=45
        )
        if success:
            self.log(f"   BOM ID: {response.get('id')}")
            self.log(f"   Components: {len(response.get('components', []))}")
            return response.get('id')
        return None

    def test_list_bom_projects(self, token):
        """Test list BOM projects"""
        success, response = self.run_test(
            "List BOM Projects",
            "GET",
            "/bom/projects",
            200,
            token=token
        )
        if success:
            self.log(f"   BOM projects count: {len(response)}")
        return success

    def test_get_bom_project(self, token, project_id):
        """Test get BOM project by ID"""
        success, response = self.run_test(
            "Get BOM Project",
            "GET",
            f"/bom/projects/{project_id}",
            200,
            token=token
        )
        return success

    def test_export_bom_csv(self, token, project_id):
        """Test export BOM as CSV"""
        success, _ = self.run_test(
            "Export BOM CSV",
            "GET",
            f"/bom/projects/{project_id}/export/csv",
            200,
            token=token
        )
        return success

    def test_export_bom_xlsx(self, token, project_id):
        """Test export BOM as XLSX"""
        success, _ = self.run_test(
            "Export BOM XLSX",
            "GET",
            f"/bom/projects/{project_id}/export/xlsx",
            200,
            token=token
        )
        return success

    def test_export_bom_pdf(self, token, project_id):
        """Test export BOM as PDF"""
        success, _ = self.run_test(
            "Export BOM PDF",
            "GET",
            f"/bom/projects/{project_id}/export/pdf",
            200,
            token=token
        )
        return success

    # ===== ADMIN TESTS =====
    def test_admin_list_users(self, token):
        """Test admin list users"""
        success, response = self.run_test(
            "Admin: List Users",
            "GET",
            "/admin/users",
            200,
            token=token
        )
        if success:
            self.log(f"   Total users: {len(response)}")
        return success

    def test_admin_api_keys_status(self, token):
        """Test admin API keys status"""
        success, response = self.run_test(
            "Admin: API Keys Status",
            "GET",
            "/admin/api-keys/status",
            200,
            token=token
        )
        if success:
            self.log(f"   Tavily: {response.get('tavily', {}).get('configured')}")
            self.log(f"   Firecrawl: {response.get('firecrawl', {}).get('configured')}")
            self.log(f"   LLM: {response.get('emergent_llm', {}).get('configured')}")
        return success

    def test_admin_list_brands(self, token):
        """Test admin list brands"""
        success, response = self.run_test(
            "Admin: List Brands",
            "GET",
            "/admin/brands",
            200,
            token=token
        )
        if success:
            self.log(f"   Total brands: {len(response)}")
        return success

    def test_admin_list_categories(self, token):
        """Test admin list categories"""
        success, response = self.run_test(
            "Admin: List Categories",
            "GET",
            "/admin/categories",
            200,
            token=token
        )
        if success:
            self.log(f"   Total categories: {len(response)}")
        return success

    def test_admin_list_products(self, token):
        """Test admin list products"""
        success, response = self.run_test(
            "Admin: List Products",
            "GET",
            "/admin/products",
            200,
            token=token
        )
        if success:
            self.log(f"   Total products: {len(response)}")
        return success

    def test_admin_list_documents(self, token):
        """Test admin list documents"""
        success, response = self.run_test(
            "Admin: List Documents",
            "GET",
            "/admin/documents",
            200,
            token=token
        )
        if success:
            self.log(f"   Total documents: {len(response)}")
        return success

    def test_admin_logs(self, token):
        """Test admin logs"""
        success, response = self.run_test(
            "Admin: View Logs",
            "GET",
            "/admin/logs?limit=10",
            200,
            token=token
        )
        if success:
            self.log(f"   Log entries: {len(response)}")
        return success

    def test_role_based_access(self):
        """Test that non-admin users cannot access admin endpoints"""
        success, _ = self.run_test(
            "RBAC: Engineer Cannot Access Admin",
            "GET",
            "/admin/users",
            403,  # Expect forbidden
            token=self.engineer_token
        )
        return success

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed} ✅")
        print(f"Tests Failed: {self.tests_failed} ❌")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.failed_tests:
            print("\nFailed Tests:")
            for test in self.failed_tests:
                print(f"  ❌ {test}")
        
        print("="*70)
        return 0 if self.tests_failed == 0 else 1


def main():
    print("="*70)
    print("EFUEL Engineering Hub - Backend API Test Suite")
    print("="*70)
    
    tester = EFUELAPITester()
    
    # Test credentials from review_request
    admin_email = "admin@efuel.com"
    admin_password = "Admin@123"
    engineer_email = "engineer@efuel.com"
    engineer_password = "Engineer@123"
    viewer_email = "viewer@efuel.com"
    viewer_password = "Viewer@123"
    
    print("\n📋 PHASE 1: HEALTH & AUTH TESTS")
    print("-" * 70)
    
    # Health check
    tester.test_health()
    
    # Login tests
    tester.admin_token = tester.test_login(admin_email, admin_password, "Admin")
    tester.engineer_token = tester.test_login(engineer_email, engineer_password, "Engineer")
    tester.viewer_token = tester.test_login(viewer_email, viewer_password, "Viewer")
    
    if not tester.admin_token or not tester.engineer_token:
        print("\n❌ CRITICAL: Login failed. Cannot proceed with further tests.")
        return tester.print_summary()
    
    # Test /me endpoint
    tester.test_me(tester.admin_token, "admin")
    tester.test_me(tester.engineer_token, "engineer")
    
    # Test registration
    tester.test_register()
    
    print("\n📋 PHASE 2: AI RESEARCH TESTS")
    print("-" * 70)
    
    # AI Search (using engineer token)
    research_id = tester.test_ai_search(tester.engineer_token, "MCB")
    if research_id:
        tester.test_get_research_by_id(tester.engineer_token, research_id)
    
    tester.test_search_history(tester.engineer_token)
    tester.test_list_cached_research(tester.engineer_token)
    
    print("\n📋 PHASE 3: COMPARE TESTS")
    print("-" * 70)
    
    tester.test_compare_products(tester.engineer_token)
    tester.test_compare_history(tester.engineer_token)
    
    print("\n📋 PHASE 4: AI CHAT TESTS")
    print("-" * 70)
    
    session_id = tester.test_chat(tester.engineer_token)
    tester.test_chat_sessions(tester.engineer_token)
    if session_id:
        tester.test_get_chat_session(tester.engineer_token, session_id)
    
    print("\n📋 PHASE 5: BOM BUILDER TESTS")
    print("-" * 70)
    
    bom_id = tester.test_generate_bom(tester.engineer_token)
    tester.test_list_bom_projects(tester.engineer_token)
    if bom_id:
        tester.test_get_bom_project(tester.engineer_token, bom_id)
        tester.test_export_bom_csv(tester.engineer_token, bom_id)
        tester.test_export_bom_xlsx(tester.engineer_token, bom_id)
        tester.test_export_bom_pdf(tester.engineer_token, bom_id)
    
    print("\n📋 PHASE 6: ADMIN PANEL TESTS")
    print("-" * 70)
    
    tester.test_admin_list_users(tester.admin_token)
    tester.test_admin_api_keys_status(tester.admin_token)
    tester.test_admin_list_brands(tester.admin_token)
    tester.test_admin_list_categories(tester.admin_token)
    tester.test_admin_list_products(tester.admin_token)
    tester.test_admin_list_documents(tester.admin_token)
    tester.test_admin_logs(tester.admin_token)
    
    print("\n📋 PHASE 7: ROLE-BASED ACCESS CONTROL TESTS")
    print("-" * 70)
    
    tester.test_role_based_access()
    
    return tester.print_summary()


if __name__ == "__main__":
    sys.exit(main())
