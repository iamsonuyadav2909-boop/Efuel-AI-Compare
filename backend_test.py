"""
EFUEL Engineering Hub - Backend API Test Suite (Updated for India Market & Single Owner)
Tests authentication changes, AI search bug fix, and India market features.
"""
import requests
import sys
import time
from datetime import datetime

class EFUELAPITester:
    def __init__(self, base_url="https://engineering-ai-3.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.owner_token = None
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
        return success, response

    def test_login(self, email, password, role_name, should_succeed=True):
        """Test login and get token"""
        expected_status = 200 if should_succeed else 401
        success, response = self.run_test(
            f"Login as {role_name} ({'should succeed' if should_succeed else 'should FAIL'})",
            "POST",
            "/auth/login",
            expected_status,
            data={"email": email, "password": password}
        )
        if success and should_succeed and 'access_token' in response:
            token = response['access_token']
            user = response.get('user', {})
            self.log(f"   Logged in: {user.get('name')} ({user.get('role')})")
            return token
        return None

    def test_register_endpoint_removed(self):
        """Test that /register endpoint no longer exists"""
        success, response = self.run_test(
            "Register Endpoint Removed (should return 404/405)",
            "POST",
            "/auth/register",
            404,  # Expect 404 Not Found since route is removed
            data={
                "name": "Test User",
                "email": "test@efuel.com",
                "password": "TestPass123!",
                "role": "engineer"
            }
        )
        # Also accept 405 Method Not Allowed
        if not success:
            # Try again expecting 405
            success2, _ = self.run_test(
                "Register Endpoint Removed (checking 405)",
                "POST",
                "/auth/register",
                405,
                data={
                    "name": "Test User",
                    "email": "test@efuel.com",
                    "password": "TestPass123!",
                    "role": "engineer"
                }
            )
            return success2
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

    # ===== RESEARCH TESTS (India Market Focus) =====
    def test_ai_search_india_market(self, token, query="RCCB"):
        """Test AI search with India market focus - takes 30-45 seconds"""
        self.log(f"Starting AI Search for '{query}' (NEW component, 30-45 seconds, testing India market + live search)...")
        success, response = self.run_test(
            f"AI Search: {query} (India Market)",
            "POST",
            "/research",
            200,
            data={"query": query, "force_refresh": True},  # Force refresh to bypass any old cache
            token=token,
            timeout=60  # Generous timeout for AI processing with live search
        )
        if success:
            category = response.get('category', '')
            products = response.get('products', [])
            data_source_mode = response.get('data_source_mode', '')
            sources = response.get('sources', [])
            confidence = response.get('confidence', 0)
            
            self.log(f"   Category: {category}")
            self.log(f"   Products: {len(products)}")
            self.log(f"   Data Source Mode: {data_source_mode}")
            self.log(f"   Sources Count: {len(sources)}")
            self.log(f"   Confidence: {confidence}")
            
            # Verify India market features
            issues = []
            
            # 1. Check data_source_mode is 'live_search' (not 'llm_knowledge')
            if data_source_mode != 'live_search':
                issues.append(f"❌ Data source mode is '{data_source_mode}' (expected 'live_search')")
            else:
                self.log(f"   ✅ Data source mode is 'live_search' (live search working)")
            
            # 2. Check sources array has actual URLs
            if len(sources) == 0:
                issues.append(f"❌ No sources found (expected live source URLs)")
            else:
                self.log(f"   ✅ Found {len(sources)} source URLs")
                # Show first 3 sources
                for i, src in enumerate(sources[:3]):
                    self.log(f"      Source {i+1}: {src.get('title', 'N/A')[:50]}... - {src.get('url', 'N/A')[:60]}")
            
            # 3. Check pricing is in INR (₹)
            inr_count = 0
            usd_count = 0
            for p in products:
                price_range = p.get('estimated_price_range', '')
                if '₹' in price_range or 'INR' in price_range.upper():
                    inr_count += 1
                if '$' in price_range or 'USD' in price_range.upper():
                    usd_count += 1
            
            if inr_count > 0:
                self.log(f"   ✅ Found {inr_count}/{len(products)} products with INR pricing")
            else:
                issues.append(f"❌ No products with INR (₹) pricing found")
            
            if usd_count > 0:
                issues.append(f"⚠️  Found {usd_count} products with USD pricing (should be INR only)")
            
            # 4. Check for Indian brands
            indian_brands = ['Havells', 'Polycab', 'RR Kabel', 'L&T', 'Legrand', 'Schneider', 
                           'Crompton', 'CG Power', 'HPL', 'Indo Asian', 'Anchor', 'Exicom',
                           'Luminous', 'Waaree', 'Vikram Solar', 'Adani Solar', 'Tata Power',
                           'UTL Solar', 'ABB', 'Siemens']
            found_indian_brands = []
            for p in products:
                brand = p.get('brand', '')
                if any(ib.lower() in brand.lower() for ib in indian_brands):
                    found_indian_brands.append(brand)
            
            if len(found_indian_brands) > 0:
                self.log(f"   ✅ Found Indian/India-available brands: {', '.join(set(found_indian_brands))}")
            else:
                issues.append(f"⚠️  No recognized Indian brands found in results")
            
            # 5. Check confidence is high (indicating live data)
            if confidence >= 0.85:
                self.log(f"   ✅ High confidence ({confidence}) indicating live search data")
            else:
                issues.append(f"⚠️  Low confidence ({confidence}) - expected ~0.9 for live search")
            
            # Print any issues found
            if issues:
                self.log("\n   INDIA MARKET VERIFICATION ISSUES:")
                for issue in issues:
                    self.log(f"   {issue}")
            
            return response.get('id'), response
        return None, {}

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

    # ===== COMPARE TESTS (INR verification) =====
    def test_compare_products_inr(self, token, products_data):
        """Test product comparison with INR verification"""
        self.log("Starting Product Comparison (30-45 seconds, checking INR)...")
        success, response = self.run_test(
            "Compare Products (INR Check)",
            "POST",
            "/compare",
            200,
            data={"products": products_data, "query_category": "RCCB"},
            token=token,
            timeout=60
        )
        if success:
            self.log(f"   Comparison ID: {response.get('id')}")
            # Check for INR mentions in comparison
            comparison_text = str(response)
            if '₹' in comparison_text or 'INR' in comparison_text.upper():
                self.log(f"   ✅ INR pricing found in comparison results")
            else:
                self.log(f"   ⚠️  No INR pricing found in comparison results")
        return success

    # ===== BOM TESTS (INR verification) =====
    def test_generate_bom_inr(self, token):
        """Test BOM generation with INR verification"""
        self.log("Starting BOM Generation for 30kW EV Charger (30-45 seconds, checking INR)...")
        success, response = self.run_test(
            "Generate BOM (30kW EV Charger, INR Check)",
            "POST",
            "/bom/generate",
            200,
            data={
                "project_name": "30kW EV Charger India",
                "requirement": "30kW EV Charger with MCB, MCCB, SPD, Energy Meter for Indian market"
            },
            token=token,
            timeout=60
        )
        if success:
            self.log(f"   BOM ID: {response.get('id')}")
            components = response.get('components', [])
            self.log(f"   Components: {len(components)}")
            
            # Check for INR in component pricing
            inr_count = 0
            for comp in components:
                price = comp.get('estimated_price', '')
                if '₹' in str(price) or 'INR' in str(price).upper():
                    inr_count += 1
            
            if inr_count > 0:
                self.log(f"   ✅ Found {inr_count}/{len(components)} components with INR pricing")
            else:
                self.log(f"   ⚠️  No INR pricing found in BOM components")
            
            return response.get('id')
        return None

    # ===== ADMIN TESTS =====
    def test_admin_list_users(self, token):
        """Test admin list users - should show exactly 1 user"""
        success, response = self.run_test(
            "Admin: List Users (should be exactly 1)",
            "GET",
            "/admin/users",
            200,
            token=token
        )
        if success:
            user_count = len(response)
            self.log(f"   Total users: {user_count}")
            if user_count == 1:
                self.log(f"   ✅ Exactly 1 user found (as expected)")
                user = response[0]
                self.log(f"   User: {user.get('name')} - {user.get('email')} - Role: {user.get('role')}")
            else:
                self.log(f"   ❌ Expected 1 user, found {user_count}")
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
            tavily = response.get('tavily', {}).get('configured', False)
            firecrawl = response.get('firecrawl', {}).get('configured', False)
            llm = response.get('emergent_llm', {}).get('configured', False)
            self.log(f"   Tavily: {tavily}, Firecrawl: {firecrawl}, LLM: {llm}")
            if tavily and firecrawl:
                self.log(f"   ✅ Live search APIs configured (Tavily + Firecrawl)")
            else:
                self.log(f"   ⚠️  Live search APIs not fully configured")
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
    print("Testing: Auth Changes, AI Search Bug Fix, India Market Features")
    print("="*70)
    
    tester = EFUELAPITester()
    
    # NEW credential (should work)
    owner_email = "owner@efuelhub.com"
    owner_password = "EfuelOwner@2026!"
    
    # OLD credentials (should all FAIL)
    old_admin_email = "admin@efuel.com"
    old_admin_password = "Admin@123"
    old_engineer_email = "engineer@efuel.com"
    old_engineer_password = "Engineer@123"
    old_viewer_email = "viewer@efuel.com"
    old_viewer_password = "Viewer@123"
    
    print("\n📋 PHASE 1: HEALTH CHECK")
    print("-" * 70)
    
    # Health check
    health_success, health_data = tester.test_health()
    
    print("\n📋 PHASE 2: AUTH TESTS (NEW vs OLD credentials)")
    print("-" * 70)
    
    # Test NEW credential (should succeed)
    tester.owner_token = tester.test_login(owner_email, owner_password, "Owner (NEW)", should_succeed=True)
    
    if not tester.owner_token:
        print("\n❌ CRITICAL: NEW owner login failed. Cannot proceed with further tests.")
        return tester.print_summary()
    
    # Test OLD credentials (should all FAIL)
    tester.test_login(old_admin_email, old_admin_password, "Admin (OLD)", should_succeed=False)
    tester.test_login(old_engineer_email, old_engineer_password, "Engineer (OLD)", should_succeed=False)
    tester.test_login(old_viewer_email, old_viewer_password, "Viewer (OLD)", should_succeed=False)
    
    # Test /me endpoint
    tester.test_me(tester.owner_token, "admin")
    
    # Test that /register endpoint is removed
    tester.test_register_endpoint_removed()
    
    print("\n📋 PHASE 3: AI SEARCH - INDIA MARKET & LIVE SEARCH BUG FIX")
    print("-" * 70)
    
    # AI Search for NEW component (RCCB) - verify live search, INR, Indian brands
    research_id, research_data = tester.test_ai_search_india_market(tester.owner_token, "RCCB")
    
    # Get search history
    tester.test_search_history(tester.owner_token)
    
    print("\n📋 PHASE 4: COMPARE ENGINE (INR verification)")
    print("-" * 70)
    
    # If we got products from research, use them for comparison
    if research_data and research_data.get('products'):
        products = research_data.get('products', [])[:2]
        compare_products = [
            {"name": p.get('name'), "brand": p.get('brand'), "category": research_data.get('category')}
            for p in products
        ]
        tester.test_compare_products_inr(tester.owner_token, compare_products)
    
    print("\n📋 PHASE 5: BOM BUILDER (INR verification)")
    print("-" * 70)
    
    bom_id = tester.test_generate_bom_inr(tester.owner_token)
    
    print("\n📋 PHASE 6: ADMIN PANEL TESTS")
    print("-" * 70)
    
    tester.test_admin_list_users(tester.owner_token)
    tester.test_admin_api_keys_status(tester.owner_token)
    tester.test_admin_list_brands(tester.owner_token)
    tester.test_admin_list_products(tester.owner_token)
    tester.test_admin_list_documents(tester.owner_token)
    
    return tester.print_summary()


if __name__ == "__main__":
    sys.exit(main())
