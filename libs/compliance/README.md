# Compliance Middleware Package

This package provides essential compliance functionality for the AI.VC investment platform, ensuring regulatory compliance and secure audit trails for investment decisions.

## Features

### 1. Investor Accreditation Verification
- Verifies that investors meet SEC accreditation requirements
- Maintains up-to-date accreditation criteria based on current regulations
- Provides clear verification results with detailed messages

### 2. OFAC Sanctions Checking
- Screens individuals and entities against OFAC sanctions lists
- Prevents transactions with sanctioned parties
- Returns detailed match results including confidence scores

### 3. Decision Payload Hashing & Audit Logging
- Creates SHA-256 hashes of all investment decision payloads
- Maintains an append-only audit log of all decisions
- Provides verification of decision integrity
- Captures complete decision context with timestamps

### 4. Admin Override System
- Role-based access control for administrative overrides
- Kill-switch functionality requiring GP-level authorization
- Comprehensive logging of all override actions
- Provides accountability for exceptional cases

## Usage

### Middleware Integration

```python
from fastapi import FastAPI
from libs.compliance import ComplianceMiddleware

app = FastAPI()

# Add the compliance middleware
app.add_middleware(ComplianceMiddleware)
```

### Verifying Investor Accreditation

```python
from libs.compliance import verify_investor_accreditation

# Check if an investor is accredited
is_accredited, message = verify_investor_accreditation("investor-123")

if is_accredited:
    # Proceed with investment processing
    pass
else:
    # Handle non-accredited investor
    pass
```

### Checking OFAC Sanctions

```python
from libs.compliance import check_ofac_sanctions

# Check if a person is on a sanctions list
name = "John Smith"
country = "United States"
is_sanctioned, result = check_ofac_sanctions(name, country)

if is_sanctioned:
    # Block the transaction
    pass
else:
    # Proceed with transaction
    pass
```

### Logging Decisions

```python
from libs.compliance import log_decision

# Log an investment decision
decision_data = {
    "investment_amount": 1000000,
    "company_id": "company-456",
    "investor_id": "investor-789",
    "decision": "approve",
    "rationale": "Strong team and product-market fit"
}

audit_result = log_decision(
    db=db_session,
    decision_type="investment",
    decision_payload=decision_data,
    user_id="analyst-123",
    company_id="company-456"
)

# Store the hash for future verification
payload_hash = audit_result["payload_hash"]
```

### Using the Admin Override

```python
# This would typically be accessed via the FastAPI router
# The router is protected with role-based access control
from fastapi import Depends
from libs.compliance.admin import admin_router, require_gp_role

# Include the admin router in your API
app.include_router(admin_router)

# Example route that implements its own override
@app.post("/custom-override")
async def custom_override(
    override_data: dict,
    role: str = Depends(require_gp_role)
):
    # Only GP role can access this endpoint
    return {"status": "override applied"}
```

## Security Considerations

- All decision hashes use SHA-256 for strong integrity protection
- Admin overrides require explicit GP role and are thoroughly logged
- The audit log is append-only to prevent modification of historical records
- All sensitive verification results are logged for future reference