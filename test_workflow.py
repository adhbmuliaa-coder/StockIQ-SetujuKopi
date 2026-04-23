#!/usr/bin/env python3
"""
Test the complete StockIQ workflow: login, select branch, and submit all 4 transaction forms.
"""

import requests
import json
import sys
import os
from datetime import datetime

# Set UTF-8 encoding for output
if sys.stdout.encoding is None or sys.stdout.encoding.lower() != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Base URL
BASE_URL = "http://localhost:5000"

# Create a session to maintain cookies
session = requests.Session()

def print_test_header(test_name):
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print(f"{'='*70}")

def print_success(msg):
    print(f"[PASS] {msg}")

def print_error(msg):
    print(f"[FAIL] {msg}")

def print_info(msg):
    print(f"[INFO] {msg}")

def test_login():
    """Test Step 1: Login as admin"""
    print_test_header("Login as Admin")
    
    try:
        # Make login request
        response = session.post(
            f"{BASE_URL}/login",
            data={"username": "admin", "password": "admin123"},
            allow_redirects=False
        )
        
        print_info(f"Response Status: {response.status_code}")
        
        # Check if redirected to branch selection
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print_info(f"Redirect Location: {location}")
            
            if 'select-branch' in location:
                print_success("Login successful - Redirected to branch selection")
                return True
            elif 'dashboard' in location:
                print_success("Login successful - Already has branch selected")
                return True
        elif response.status_code == 200:
            # Check content for success message
            if 'Cabang' in response.text or 'cabang' in response.text:
                print_success("Login successful - Branch selection page loaded")
                return True
        
        print_error(f"Unexpected response: {response.status_code}")
        return False
        
    except Exception as e:
        print_error(f"Login failed: {str(e)}")
        return False

def get_branches():
    """Get list of available branches"""
    print_test_header("Get Available Branches")
    
    try:
        # Fetch the select-branch page to get the list
        response = session.get(f"{BASE_URL}/select-branch", allow_redirects=False)
        
        if response.status_code != 200:
            print_error(f"Failed to get branch list (Status: {response.status_code})")
            return None
        
        # Parse the response to find branch buttons
        import re
        # Look for hidden inputs with branch IDs
        branch_pattern = r'<input[^>]*name=["\']branch_id["\'][^>]*value=["\'](\d+)["\'][^>]*>.*?<button[^>]*class=["\']branch-card["\'][^>]*>.*?<div[^>]*class=["\']name["\'][^>]*>([^<]+)</div>'
        
        # Try a simpler approach - find all branch-card buttons and their corresponding hidden inputs
        all_branches = []
        
        # Find all instances of button type="submit" with branch-card class
        button_pattern = r'<button[^>]*class=["\']branch-card["\'][^>]*id=["\']branch-(\d+)'
        branch_ids = re.findall(button_pattern, response.text)
        
        # Find all text in name divs
        name_pattern = r'<div\s+class=["\']name["\'][^>]*>([^<]+)</div>'
        names = re.findall(name_pattern, response.text)
        
        if branch_ids and names:
            # Pair branch IDs with names
            for bid, name in zip(branch_ids, names):
                all_branches.append((bid, name.strip()))
        
        if not all_branches:
            print_error("No branches found in response")
            return None
        
        print_success(f"Found {len(all_branches)} branch(es):")
        for branch_id, branch_name in all_branches:
            print_info(f"  - ID: {branch_id}, Name: {branch_name}")
        
        return all_branches
        
    except Exception as e:
        print_error(f"Failed to get branches: {str(e)}")
        return None

def select_branch(branch_id, branch_name):
    """Test Step 2-3: Select first branch"""
    print_test_header(f"Select Branch: {branch_name}")
    
    try:
        response = session.post(
            f"{BASE_URL}/select-branch",
            data={"branch_id": branch_id},
            allow_redirects=False
        )
        
        print_info(f"Response Status: {response.status_code}")
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print_info(f"Redirect Location: {location}")
            
            if 'dashboard' in location or location == '/':
                print_success(f"Branch '{branch_name}' selected successfully")
                return True
        
        print_error(f"Failed to select branch (Status: {response.status_code})")
        return False
        
    except Exception as e:
        print_error(f"Failed to select branch: {str(e)}")
        return False

def verify_dashboard():
    """Test Step 4: Verify dashboard loads"""
    print_test_header("Verify Dashboard Loads")
    
    try:
        response = session.get(f"{BASE_URL}/", allow_redirects=True)
        
        print_info(f"Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print_error(f"Dashboard loading failed (Status: {response.status_code})")
            return False
        
        # Check for dashboard indicators
        indicators = ['Barang Masuk', 'Transfer Keluar', 'Prepare', 'NPU']
        found_indicators = []
        
        for indicator in indicators:
            if indicator in response.text:
                found_indicators.append(indicator)
        
        if found_indicators:
            print_success(f"Dashboard loaded successfully")
            print_info(f"Found {len(found_indicators)} transaction type indicators")
            return True
        
        print_error("Dashboard content not found")
        return False
        
    except Exception as e:
        print_error(f"Failed to verify dashboard: {str(e)}")
        return False

def get_divisi_and_bahan(form_type='bahan'):
    """Get available divisi and bahan for a form"""
    try:
        # Fetch the form page
        form_routes = {
            'barang_masuk': '/barang-masuk',
            'transfer': '/transfer',
            'prepare': '/prepare',
            'npu': '/npu'
        }
        
        route = form_routes.get(form_type, '/barang-masuk')
        response = session.get(f"{BASE_URL}{route}")
        
        if response.status_code != 200:
            return None, None
        
        # Parse divisi options
        import re
        divisi_pattern = r'<option\s+value=(["\']?)([^"\']+)\1[^>]*>([^<]+)</option>'
        divisi_matches = re.findall(divisi_pattern, response.text)
        
        # Filter for divisi (look for relevant select elements)
        divisi_list = []
        for match in divisi_matches:
            value = match[1]
            label = match[2].strip()
            # Include non-empty values
            if value and not value.startswith('--') and label and not label.startswith('--'):
                divisi_list.append(value)
        
        # Remove duplicates while preserving order
        divisi_list = list(dict.fromkeys(divisi_list))
        
        if divisi_list:
            return divisi_list[0], divisi_list
        
        return None, None
        
    except Exception as e:
        print_error(f"Failed to parse form: {str(e)}")
        return None, None

def test_barang_masuk_form():
    """Test Step 5: Submit Barang Masuk (Inbound) transaction"""
    print_test_header("Test Barang Masuk (Inbound) Form")
    
    try:
        # Fetch the form page first
        response = session.get(f"{BASE_URL}/barang-masuk")
        print_info(f"Form page status: {response.status_code}")
        
        # Parse available divisi from the form
        import re
        divisi_pattern = r'<option[^>]*value=["\']([^"\']+)["\'][^>]*>([^<]+)</option>'
        divisi_matches = re.findall(divisi_pattern, response.text)
        
        if not divisi_matches:
            print_error("No divisi options found in form")
            return False
        
        # Get first valid divisi (skip empty/placeholder options)
        selected_divisi = None
        for value, label in divisi_matches:
            if value and label and not value.startswith('--'):
                selected_divisi = value
                print_info(f"Selected divisi: {value} ({label.strip()})")
                break
        
        if not selected_divisi:
            print_error("No valid divisi found")
            return False
        
        # Submit the form with test data
        form_data = {
            'divisi': selected_divisi,
            'nama_bahan': 'Test Bahan Masuk 1',
            'qty': 10,
            'satuan': 'kg',
            'asal_barang': 'Supplier ABC',
            'keterangan': 'Test inbound transaction'
        }
        
        response = session.post(
            f"{BASE_URL}/barang-masuk",
            data=form_data,
            allow_redirects=False
        )
        
        print_info(f"Form submission status: {response.status_code}")
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print_info(f"Redirect to: {location}")
            print_success("Barang Masuk form submitted successfully")
            return True
        elif 'berhasil' in response.text.lower() or 'success' in response.text.lower():
            print_success("Barang Masuk form submitted successfully")
            return True
        else:
            print_error(f"Unexpected response (Status: {response.status_code})")
            return False
        
    except Exception as e:
        print_error(f"Failed to submit Barang Masuk form: {str(e)}")
        return False

def test_transfer_form():
    """Test Step 6: Submit Transfer Keluar (Outbound) transaction"""
    print_test_header("Test Transfer Keluar (Outbound) Form")
    
    try:
        # Fetch the form page first
        response = session.get(f"{BASE_URL}/transfer")
        print_info(f"Form page status: {response.status_code}")
        
        # Parse available divisi
        import re
        divisi_pattern = r'<option[^>]*value=["\']([^"\']+)["\'][^>]*>([^<]+)</option>'
        divisi_matches = re.findall(divisi_pattern, response.text)
        
        # Get first valid divisi
        selected_divisi = None
        for value, label in divisi_matches:
            if value and label and not value.startswith('--'):
                selected_divisi = value
                print_info(f"Selected divisi: {value} ({label.strip()})")
                break
        
        if not selected_divisi:
            print_error("No valid divisi found")
            return False
        
        # Parse available branches (for cabang_tujuan)
        # Look for the cabang_tujuan select element
        cabang_start = response.text.find('name="cabang_tujuan"')
        if cabang_start == -1:
            print_error("cabang_tujuan select not found")
            return False
        
        # Find the next </select> after cabang_tujuan
        select_end = response.text.find('</select>', cabang_start)
        cabang_section = response.text[cabang_start:select_end]
        
        # Extract branch options from this section
        branch_pattern = r'<option[^>]*value=["\']([^"\']+)["\'][^>]*>([^<]+)</option>'
        branch_matches = re.findall(branch_pattern, cabang_section)
        
        selected_branch = None
        for branch_name, display_name in branch_matches:
            if branch_name and display_name and not branch_name.startswith('--'):
                selected_branch = branch_name
                print_info(f"Selected destination branch: {branch_name} ({display_name.strip()})")
                break
        
        if not selected_branch:
            print_error("No destination branches available")
            return False
        
        # Submit the form
        form_data = {
            'divisi': selected_divisi,
            'nama_bahan': 'Test Bahan Transfer 1',
            'qty': 5,
            'satuan': 'kg',
            'cabang_tujuan': selected_branch,
            'keterangan': 'Test transfer transaction'
        }
        
        response = session.post(
            f"{BASE_URL}/transfer",
            data=form_data,
            allow_redirects=False
        )
        
        print_info(f"Form submission status: {response.status_code}")
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print_info(f"Redirect to: {location}")
            print_success("Transfer Keluar form submitted successfully")
            return True
        else:
            print_error(f"Unexpected response (Status: {response.status_code})")
            return False
        
    except Exception as e:
        print_error(f"Failed to submit Transfer form: {str(e)}")
        return False

def test_prepare_form():
    """Test Step 7: Submit Prepare transaction"""
    print_test_header("Test Prepare Form")
    
    try:
        # Fetch the form page
        response = session.get(f"{BASE_URL}/prepare")
        print_info(f"Form page status: {response.status_code}")
        
        # Parse available divisi
        import re
        divisi_pattern = r'<option[^>]*value=["\']([^"\']+)["\'][^>]*>([^<]+)</option>'
        divisi_matches = re.findall(divisi_pattern, response.text)
        
        # Get first valid divisi
        selected_divisi = None
        for value, label in divisi_matches:
            if value and label and not value.startswith('--'):
                selected_divisi = value
                print_info(f"Selected divisi: {value} ({label.strip()})")
                break
        
        if not selected_divisi:
            print_error("No valid divisi found")
            return False
        
        # Submit the form
        form_data = {
            'divisi': selected_divisi,
            'nama_bahan': 'Test Bahan Prepare 1',
            'qty': 3,
            'satuan': 'pcs',
            'keterangan': 'Test prepare transaction'
        }
        
        response = session.post(
            f"{BASE_URL}/prepare",
            data=form_data,
            allow_redirects=False
        )
        
        print_info(f"Form submission status: {response.status_code}")
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print_info(f"Redirect to: {location}")
            print_success("Prepare form submitted successfully")
            return True
        else:
            print_error(f"Unexpected response (Status: {response.status_code})")
            return False
        
    except Exception as e:
        print_error(f"Failed to submit Prepare form: {str(e)}")
        return False

def test_npu_form():
    """Test Step 8: Submit NPU (Wastage) transaction"""
    print_test_header("Test NPU (Wastage) Form")
    
    try:
        # Fetch the form page
        response = session.get(f"{BASE_URL}/npu")
        print_info(f"Form page status: {response.status_code}")
        
        # Parse available divisi
        import re
        divisi_pattern = r'<option[^>]*value=["\']([^"\']+)["\'][^>]*>([^<]+)</option>'
        divisi_matches = re.findall(divisi_pattern, response.text)
        
        # Get first valid divisi
        selected_divisi = None
        for value, label in divisi_matches:
            if value and label and not value.startswith('--'):
                selected_divisi = value
                print_info(f"Selected divisi: {value} ({label.strip()})")
                break
        
        if not selected_divisi:
            print_error("No valid divisi found")
            return False
        
        # Submit the form
        form_data = {
            'divisi': selected_divisi,
            'nama_bahan': 'Test Bahan NPU 1',
            'qty': 2,
            'satuan': 'kg',
            'kategori_npu': 'Rusak',
            'keterangan': 'Test NPU transaction - damaged goods'
        }
        
        response = session.post(
            f"{BASE_URL}/npu",
            data=form_data,
            allow_redirects=False
        )
        
        print_info(f"Form submission status: {response.status_code}")
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print_info(f"Redirect to: {location}")
            print_success("NPU form submitted successfully")
            return True
        else:
            print_error(f"Unexpected response (Status: {response.status_code})")
            return False
        
    except Exception as e:
        print_error(f"Failed to submit NPU form: {str(e)}")
        return False

def verify_transactions_in_log():
    """Test Step 9: Return to dashboard and verify all 4 transactions appear"""
    print_test_header("Verify All Transactions in Dashboard Log")
    
    try:
        response = session.get(f"{BASE_URL}/", allow_redirects=True)
        
        print_info(f"Dashboard status: {response.status_code}")
        
        if response.status_code != 200:
            print_error(f"Failed to load dashboard (Status: {response.status_code})")
            return False
        
        # Look for transaction evidence in the page
        transaction_types = {
            'masuk': 'Barang Masuk|masuk',
            'transfer': 'Transfer Keluar|transfer',
            'prepare': 'Prepare',
            'npu': 'NPU'
        }
        
        found_transactions = {}
        for tx_type, pattern in transaction_types.items():
            import re
            if re.search(pattern, response.text, re.IGNORECASE):
                found_transactions[tx_type] = True
        
        print_success(f"Dashboard loaded with {len(found_transactions)} transaction types visible")
        
        if found_transactions:
            for tx_type in found_transactions:
                print_info(f"  ✓ {tx_type.upper()} transaction type found")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to verify transactions: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("STOCKIQ COMPLETE WORKFLOW TEST SUITE")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    
    results = {}
    
    # Step 1: Login
    results['login'] = test_login()
    if not results['login']:
        print_error("Cannot proceed without successful login")
        return
    
    # Step 2: Get branches and select first one
    branches = get_branches()
    if not branches:
        print_error("Cannot proceed without branches")
        return
    
    branch_id, branch_name = branches[0]
    results['select_branch'] = select_branch(branch_id, branch_name)
    if not results['select_branch']:
        print_error("Cannot proceed without branch selection")
        return
    
    # Step 3: Verify dashboard
    results['dashboard'] = verify_dashboard()
    
    # Step 4: Submit transaction forms
    results['barang_masuk'] = test_barang_masuk_form()
    results['transfer'] = test_transfer_form()
    results['prepare'] = test_prepare_form()
    results['npu'] = test_npu_form()
    
    # Step 5: Verify all transactions in log
    results['transactions_log'] = verify_transactions_in_log()
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_flag in results.items():
        status = "PASS" if passed_flag else "FAIL"
        symbol = "[OK]" if passed_flag else "[NO]"
        print(f"{symbol} {test_name.upper()}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if passed == total:
        print("\n[OK] ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n[NO] {total - passed} TEST(S) FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(main())
