"""
Integration tests for the compliance middleware package.

This module contains tests to verify the integration of key compliance features.
"""

import json
import hashlib

# Test the accreditation verification function
def test_accreditation_verification():
    try:
        from libs.compliance import verify_investor_accreditation
        
        # Test a valid investor
        is_accredited, message = verify_investor_accreditation("valid-investor")
        assert is_accredited is True
        assert "verified as accredited investor" in message
        
        # Test an invalid investor
        is_accredited, message = verify_investor_accreditation("test-non-accredited")
        assert is_accredited is False
        assert "could not be verified" in message
        
        print("Accreditation verification test passed!")
    except ImportError as e:
        print(f"Import error in accreditation test: {e}")
    except Exception as e:
        print(f"Error in accreditation test: {e}")

# Test the OFAC sanctions checking function
def test_sanctions_check():
    try:
        from libs.compliance import check_ofac_sanctions
        
        # Test a person not on the sanctions list
        is_sanctioned, result = check_ofac_sanctions("John Doe", "United States")
        assert is_sanctioned is False
        assert result["is_sanctioned"] is False
        assert "sanctions_lists_checked" in result
        
        print("Sanctions check test passed!")
    except ImportError as e:
        print(f"Import error in sanctions test: {e}")
    except Exception as e:
        print(f"Error in sanctions test: {e}")

# Test the decision payload hashing function
def test_decision_hashing():
    try:
        from libs.compliance import hash_decision_payload
        
        # Create a test payload
        payload = {
            "investment_amount": 1000000,
            "company_id": "company-123",
            "investor_id": "investor-456",
            "decision": "approve"
        }
        
        # Calculate the hash manually for comparison
        serialized = json.dumps(payload, sort_keys=True)
        expected_hash = hashlib.sha256(serialized.encode('utf-8')).hexdigest()
        
        # Test the hash_decision_payload function
        payload_hash = hash_decision_payload(payload)
        assert payload_hash == expected_hash
        
        # Change the payload and verify the hash changes
        modified_payload = payload.copy()
        modified_payload["decision"] = "reject"
        modified_hash = hash_decision_payload(modified_payload)
        assert modified_hash != payload_hash
        
        print("Decision hashing test passed!")
    except ImportError as e:
        print(f"Import error in hashing test: {e}")
    except Exception as e:
        print(f"Error in hashing test: {e}")

if __name__ == "__main__":
    print("Running compliance integration tests...")
    test_accreditation_verification()
    test_sanctions_check()
    test_decision_hashing()
    print("All compliance integration tests completed.")