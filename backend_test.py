"""
EFUEL Engineering Hub - Backend API Test Suite (Phase A: Strict Live-Search-Only)
Tests the STRICT live-search-only research pipeline with zero hallucination tolerance.
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
        self.critical_issues = []

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

    # ===== HEALTH & CONFIG TESTS =====
    def test_health(self):
        """Test health endpoint - verify Exa NOT configured, Tavily/Firecrawl/LLM configured"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "/health",
            200
        )
        if success:
            exa = response.get('exa_configured', None)
            tavily = response.get('tavily_configured', None)
            firecrawl = response.get('firecrawl_configured', None)
            llm = response.get('llm_configured', None)
            
            self.log(f"   Exa: {exa}, Tavily: {tavily}, Firecrawl: {firecrawl}, LLM: {llm}")
            
            # Verify expected configuration
            issues = []
            if exa is not False:
                issues.append(f"❌ Exa should be False (not configured), got: {exa}")
            else:
                self.log(f"   ✅ Exa correctly NOT configured (will use Tavily fallback)")
            
            if tavily is not True:
                issues.append(f"❌ Tavily should be True (configured), got: {tavily}")
                self.critical_issues.append("Tavily API not configured")
            else:
                self.log(f"   ✅ Tavily configured (fallback search provider)")
            
            if firecrawl is not True:
                issues.append(f"❌ Firecrawl should be True (configured), got: {firecrawl}")
                self.critical_issues.append("Firecrawl API not configured")
            else:
                self.log(f"   ✅ Firecrawl configured (content extraction)")
            
            if llm is not True:
                issues.append(f"❌ LLM should be True (configured), got: {llm}")
                self.critical_issues.append("LLM API not configured")
            else:
                self.log(f"   ✅ LLM configured (AI analysis)")
            
            if issues:
                for issue in issues:
                    self.log(f"   {issue}", "FAIL")
            
        return success, response

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
            return token
        return None

    # ===== RESEARCH TESTS (STRICT LIVE-SEARCH-ONLY) =====
    def test_research_real_component(self, token, query="MCB"):
        """Test research with REAL component - verify live_search mode, tavily provider, source_urls"""
        self.log(f"Starting AI Research for REAL component '{query}' (30-60 seconds)...")
        success, response = self.run_test(
            f"Research: {query} (REAL component)",
            "POST",
            "/research",
            200,
            data={"query": query, "force_refresh": True},
            token=token,
            timeout=70
        )
        
        if success:
            data_source_mode = response.get('data_source_mode', '')
            no_data = response.get('no_data', None)
            search_provider_used = response.get('search_provider_used', '')
            products = response.get('products', [])
            last_crawl_time = response.get('last_crawl_time', None)
            message = response.get('message', '')
            
            self.log(f"   Data Source Mode: {data_source_mode}")
            self.log(f"   No Data: {no_data}")
            self.log(f"   Search Provider: {search_provider_used}")
            self.log(f"   Products Count: {len(products)}")
            self.log(f"   Last Crawl Time: {last_crawl_time}")
            
            # CRITICAL VERIFICATIONS
            issues = []
            
            # 1. data_source_mode MUST be 'live_search'
            if data_source_mode != 'live_search':
                issues.append(f"❌ CRITICAL: data_source_mode is '{data_source_mode}' (expected 'live_search')")
                self.critical_issues.append(f"Research for '{query}' returned wrong data_source_mode: {data_source_mode}")
            else:
                self.log(f"   ✅ data_source_mode is 'live_search'")
            
            # 2. no_data MUST be False
            if no_data is not False:
                issues.append(f"❌ CRITICAL: no_data is {no_data} (expected False)")
                self.critical_issues.append(f"Research for '{query}' returned no_data={no_data}")
            else:
                self.log(f"   ✅ no_data is False")
            
            # 3. search_provider_used MUST be 'tavily' (since Exa not configured)
            if search_provider_used != 'tavily':
                issues.append(f"❌ search_provider_used is '{search_provider_used}' (expected 'tavily' since Exa not configured)")
            else:
                self.log(f"   ✅ search_provider_used is 'tavily' (correct fallback)")
            
            # 4. products array MUST be non-empty
            if len(products) == 0:
                issues.append(f"❌ CRITICAL: products array is EMPTY (expected 1-5 products)")
                self.critical_issues.append(f"Research for '{query}' returned ZERO products")
            else:
                self.log(f"   ✅ products array has {len(products)} products")
            
            # 5. Each product MUST have non-empty source_urls
            for i, p in enumerate(products):
                source_urls = p.get('source_urls', [])
                if not source_urls or len(source_urls) == 0:
                    issues.append(f"❌ CRITICAL: Product {i+1} '{p.get('name')}' has EMPTY source_urls (violates grounding requirement)")
                    self.critical_issues.append(f"Product '{p.get('name')}' has no source_urls")
                else:
                    self.log(f"   ✅ Product {i+1} '{p.get('name')}' has {len(source_urls)} source URLs")
            
            # 6. last_crawl_time MUST be populated
            if not last_crawl_time:
                issues.append(f"❌ last_crawl_time is NULL (expected ISO timestamp)")
            else:
                self.log(f"   ✅ last_crawl_time populated: {last_crawl_time}")
            
            # 7. message should be EMPTY (only populated for no_data)
            if message:
                issues.append(f"⚠️  message field is populated ('{message[:50]}...') but should be empty for successful results")
            
            if issues:
                self.log("\n   VERIFICATION ISSUES:")
                for issue in issues:
                    self.log(f"   {issue}")
            
            return response.get('id'), response
        
        return None, {}

    def test_research_nonsense_query(self, token):
        """Test research with NONSENSE query - verify no_data=true, exact message"""
        nonsense_query = "zzxxqqasdkjqwe12312 fictional nonexistent gadget"
        self.log(f"Starting AI Research for NONSENSE query '{nonsense_query}' (should return no_data)...")
        
        success, response = self.run_test(
            f"Research: Nonsense Query (should return no_data)",
            "POST",
            "/research",
            200,
            data={"query": nonsense_query, "force_refresh": False},
            token=token,
            timeout=70
        )
        
        if success:
            data_source_mode = response.get('data_source_mode', '')
            no_data = response.get('no_data', None)
            products = response.get('products', [])
            message = response.get('message', '')
            
            self.log(f"   Data Source Mode: {data_source_mode}")
            self.log(f"   No Data: {no_data}")
            self.log(f"   Products Count: {len(products)}")
            self.log(f"   Message: {message[:100]}...")
            
            # CRITICAL VERIFICATIONS
            issues = []
            
            # Expected exact message
            EXPECTED_MESSAGE = "No verified live manufacturer data was found for this product. Please check your search query or configure Exa/Tavily and Firecrawl API keys."
            
            # 1. no_data MUST be True
            if no_data is not True:
                issues.append(f"❌ CRITICAL: no_data is {no_data} (expected True)")
                self.critical_issues.append(f"Nonsense query returned no_data={no_data} instead of True")
            else:
                self.log(f"   ✅ no_data is True")
            
            # 2. data_source_mode MUST be 'no_data'
            if data_source_mode != 'no_data':
                issues.append(f"❌ CRITICAL: data_source_mode is '{data_source_mode}' (expected 'no_data')")
                self.critical_issues.append(f"Nonsense query returned data_source_mode='{data_source_mode}' instead of 'no_data'")
            else:
                self.log(f"   ✅ data_source_mode is 'no_data'")
            
            # 3. products array MUST be empty
            if len(products) != 0:
                issues.append(f"❌ CRITICAL: products array has {len(products)} products (expected 0)")
                self.critical_issues.append(f"Nonsense query returned {len(products)} products instead of 0")
            else:
                self.log(f"   ✅ products array is empty")
            
            # 4. message MUST EXACTLY match the expected message
            if message != EXPECTED_MESSAGE:
                issues.append(f"❌ CRITICAL: message does NOT match expected exact message")
                self.log(f"   Expected: '{EXPECTED_MESSAGE}'", "FAIL")
                self.log(f"   Got:      '{message}'", "FAIL")
                self.critical_issues.append(f"Nonsense query message mismatch")
            else:
                self.log(f"   ✅ message EXACTLY matches expected strict message")
            
            if issues:
                self.log("\n   VERIFICATION ISSUES:")
                for issue in issues:
                    self.log(f"   {issue}")
            
            return response
        
        return {}

    def test_cache_behavior(self, token, query="Solar Inverter"):
        """Test cache behavior - verify no_data results NOT cached"""
        self.log(f"Testing cache behavior with query '{query}'...")
        
        # First request (should be fresh)
        self.log(f"   First request (fresh)...")
        success1, response1 = self.run_test(
            f"Cache Test: First Request ({query})",
            "POST",
            "/research",
            200,
            data={"query": query, "force_refresh": True},
            token=token,
            timeout=70
        )
        
        if not success1:
            self.log(f"   ❌ First request failed, cannot test cache", "FAIL")
            return False
        
        time.sleep(2)
        
        # Second request (should be cached if successful)
        self.log(f"   Second request (should be cached if first was successful)...")
        start_time = time.time()
        success2, response2 = self.run_test(
            f"Cache Test: Second Request ({query})",
            "POST",
            "/research",
            200,
            data={"query": query, "force_refresh": False},
            token=token,
            timeout=70
        )
        elapsed = time.time() - start_time
        
        if success2:
            no_data1 = response1.get('no_data', False)
            no_data2 = response2.get('no_data', False)
            
            if not no_data1:
                # Successful result - should be cached (fast response)
                if elapsed < 5:
                    self.log(f"   ✅ Cache HIT detected (response in {elapsed:.2f}s)")
                else:
                    self.log(f"   ⚠️  Cache may have MISSED (response took {elapsed:.2f}s)")
            else:
                # no_data result - should NOT be cached (fresh attempt)
                self.log(f"   ✅ no_data result correctly NOT cached (fresh attempt made)")
        
        return success2

    # ===== ADMIN TESTS =====
    def test_admin_api_keys_status(self, token):
        """Test admin API keys status - verify all providers have required fields"""
        success, response = self.run_test(
            "Admin: API Keys Status",
            "GET",
            "/admin/api-keys/status",
            200,
            token=token
        )
        
        if success:
            providers = ['exa', 'tavily', 'firecrawl', 'emergent_llm']
            required_fields = ['configured', 'enabled', 'source', 'usage_count', 'last_success_at']
            
            issues = []
            for provider in providers:
                provider_data = response.get(provider, {})
                self.log(f"   {provider}: configured={provider_data.get('configured')}, enabled={provider_data.get('enabled')}, source={provider_data.get('source')}")
                
                for field in required_fields:
                    if field not in provider_data:
                        issues.append(f"❌ {provider} missing field '{field}'")
            
            if issues:
                self.log("\n   API KEYS STATUS ISSUES:")
                for issue in issues:
                    self.log(f"   {issue}")
            else:
                self.log(f"   ✅ All providers have required fields")
        
        return success

    def test_dashboard_summary(self, token):
        """Test dashboard summary - verify api_status includes exa_search key"""
        success, response = self.run_test(
            "Dashboard: Summary",
            "GET",
            "/dashboard/summary",
            200,
            token=token
        )
        
        if success:
            api_status = response.get('api_status', {})
            self.log(f"   API Status keys: {list(api_status.keys())}")
            
            required_keys = ['exa_search', 'tavily_search', 'firecrawl_extract', 'ai_analysis']
            issues = []
            
            for key in required_keys:
                if key not in api_status:
                    issues.append(f"❌ api_status missing key '{key}'")
                else:
                    self.log(f"   {key}: {api_status[key]}")
            
            if issues:
                self.log("\n   DASHBOARD API STATUS ISSUES:")
                for issue in issues:
                    self.log(f"   {issue}")
            else:
                self.log(f"   ✅ api_status has all required keys including exa_search")
        
        return success

    # ===== REGRESSION TESTS =====
    def test_regression_compare(self, token, products_data):
        """Regression: Compare API"""
        success, response = self.run_test(
            "Regression: Compare API",
            "POST",
            "/compare",
            200,
            data={"products": products_data, "query_category": "MCB"},
            token=token,
            timeout=60
        )
        if success:
            self.log(f"   ✅ Compare API working")
        return success

    def test_regression_bom(self, token):
        """Regression: BOM Generate API"""
        success, response = self.run_test(
            "Regression: BOM Generate API",
            "POST",
            "/bom/generate",
            200,
            data={
                "project_name": "Test EV Charger",
                "requirement": "10kW EV Charger with MCB and MCCB"
            },
            token=token,
            timeout=60
        )
        if success:
            self.log(f"   ✅ BOM Generate API working")
        return success

    def test_regression_chat(self, token):
        """Regression: Chat API"""
        success, response = self.run_test(
            "Regression: Chat API",
            "POST",
            "/chat",
            200,
            data={"message": "What is an MCB?"},
            token=token,
            timeout=30
        )
        if success:
            self.log(f"   ✅ Chat API working")
        return success

    def test_regression_favorites(self, token):
        """Regression: Favorites API"""
        success, response = self.run_test(
            "Regression: List Favorites",
            "GET",
            "/favorites",
            200,
            token=token
        )
        if success:
            self.log(f"   ✅ Favorites API working")
        return success

    def test_regression_documents(self, token):
        """Regression: Documents API"""
        success, response = self.run_test(
            "Regression: List Documents",
            "GET",
            "/documents",
            200,
            token=token
        )
        if success:
            self.log(f"   ✅ Documents API working")
        return success

    def test_regression_products(self, token):
        """Regression: Products API"""
        success, response = self.run_test(
            "Regression: List Products",
            "GET",
            "/products",
            200,
            token=token
        )
        if success:
            self.log(f"   ✅ Products API working")
        return success

    def test_regression_brands(self, token):
        """Regression: Brands API"""
        success, response = self.run_test(
            "Regression: List Brands",
            "GET",
            "/brands",
            200,
            token=token
        )
        if success:
            self.log(f"   ✅ Brands API working")
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
    print("Phase A: STRICT Live-Search-Only Research Engine")
    print("="*70)
    
    tester = EFUELAPITester()
    
    # Credentials from review_request
    owner_email = "owner@efuelhub.com"
    owner_password = "EfuelOwner@2026!"
    
    print("\n📋 PHASE 1: HEALTH & CONFIGURATION CHECK")
    print("-" * 70)
    
    health_success, health_data = tester.test_health()
    
    print("\n📋 PHASE 2: AUTHENTICATION")
    print("-" * 70)
    
    tester.owner_token = tester.test_login(owner_email, owner_password, "Owner")
    
    if not tester.owner_token:
        print("\n❌ CRITICAL: Login failed. Cannot proceed with further tests.")
        return tester.print_summary()
    
    print("\n📋 PHASE 3: RESEARCH ENGINE - REAL COMPONENT QUERIES")
    print("-" * 70)
    
    # Test with multiple real components
    research_id1, research_data1 = tester.test_research_real_component(tester.owner_token, "MCB")
    time.sleep(2)
    research_id2, research_data2 = tester.test_research_real_component(tester.owner_token, "Solar Inverter")
    time.sleep(2)
    research_id3, research_data3 = tester.test_research_real_component(tester.owner_token, "EV Connector")
    
    print("\n📋 PHASE 4: RESEARCH ENGINE - NONSENSE QUERY (NO DATA)")
    print("-" * 70)
    
    tester.test_research_nonsense_query(tester.owner_token)
    
    print("\n📋 PHASE 5: CACHE BEHAVIOR")
    print("-" * 70)
    
    tester.test_cache_behavior(tester.owner_token, "MCCB")
    
    print("\n📋 PHASE 6: ADMIN PANEL - API KEYS & DASHBOARD")
    print("-" * 70)
    
    tester.test_admin_api_keys_status(tester.owner_token)
    tester.test_dashboard_summary(tester.owner_token)
    
    print("\n📋 PHASE 7: REGRESSION TESTS")
    print("-" * 70)
    
    # Use products from first research for compare test
    if research_data1 and research_data1.get('products'):
        products = research_data1.get('products', [])[:2]
        compare_products = [
            {"name": p.get('name'), "brand": p.get('brand'), "category": research_data1.get('category')}
            for p in products
        ]
        tester.test_regression_compare(tester.owner_token, compare_products)
    
    tester.test_regression_bom(tester.owner_token)
    tester.test_regression_chat(tester.owner_token)
    tester.test_regression_favorites(tester.owner_token)
    tester.test_regression_documents(tester.owner_token)
    tester.test_regression_products(tester.owner_token)
    tester.test_regression_brands(tester.owner_token)
    
    return tester.print_summary()


if __name__ == "__main__":
    sys.exit(main())
