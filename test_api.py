#!/usr/bin/env python3
"""
Simple test script for the Canadian Wire Transfer Simulator API
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running?")
        return False

def test_create_transfer():
    """Test creating a transfer"""
    print("🔍 Testing transfer creation...")
    
    transfer_data = {
        "debtor_name": "John Doe",
        "institution_number": "003",
        "transit_number": "12345",
        "account_number": "1234567890",
        "creditor_name": "Jane Smith",
        "creditor_iban": "DE89370400440532013000",
        "creditor_bic": "COBADEFFXXX",
        "amount": 1000.00,
        "currency": "CAD",
        "purpose": "Payment for services"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/create_transfer", 
                               json=transfer_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Transfer created successfully")
            print(f"   Transfer ID: {data['transfer_id']}")
            return data['transfer_id']
        else:
            print(f"❌ Transfer creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating transfer: {e}")
        return None

def test_list_transfers():
    """Test listing transfers"""
    print("🔍 Testing transfer listing...")
    try:
        response = requests.get(f"{BASE_URL}/transfers")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['count']} transfers")
            return True
        else:
            print(f"❌ Transfer listing failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error listing transfers: {e}")
        return False

def test_get_transfer(transfer_id):
    """Test getting a specific transfer"""
    print(f"🔍 Testing transfer details for {transfer_id}...")
    try:
        response = requests.get(f"{BASE_URL}/transfer/{transfer_id}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Transfer details retrieved successfully")
            print(f"   Debtor: {data['debtor_name']}")
            print(f"   Creditor: {data['creditor_name']}")
            print(f"   Amount: {data['amount']} {data['currency']}")
            print(f"   XML Length: {len(data['pacs_008_xml'])} characters")
            return True
        else:
            print(f"❌ Transfer details failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting transfer details: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Canadian Wire Transfer Simulator API")
    print("=" * 50)
    
    # Test health check
    if not test_health_check():
        print("\n❌ Health check failed. Please ensure the server is running.")
        return
    
    print()
    
    # Test transfer creation
    transfer_id = test_create_transfer()
    if not transfer_id:
        print("\n❌ Transfer creation failed.")
        return
    
    print()
    
    # Test listing transfers
    test_list_transfers()
    
    print()
    
    # Test getting transfer details
    test_get_transfer(transfer_id)
    
    print()
    print("🎉 All tests completed!")

if __name__ == "__main__":
    main() 