#!/bin/bash
# MedVision AI Sprint 2 - Complete API Test Suite
# Run from inside the backend container: bash /app/test_sprint2.sh

BASE="http://localhost:8000/api/v1"
PASS=0
FAIL=0

check() {
  local desc="$1" expected="$2" actual="$3"
  if [[ "$actual" == "$expected" ]]; then
    echo "  PASS: $desc"
    ((PASS++))
  else
    echo "  FAIL: $desc (expected=$expected, got=$actual)"
    ((FAIL++))
  fi
}

check_contains() {
  local desc="$1" pattern="$2" actual="$3"
  if echo "$actual" | grep -q "$pattern"; then
    echo "  PASS: $desc"
    ((PASS++))
  else
    echo "  FAIL: $desc (pattern '$pattern' not found in: $actual)"
    ((FAIL++))
  fi
}

check_not_contains() {
  local desc="$1" pattern="$2" actual="$3"
  if ! echo "$actual" | grep -q "$pattern"; then
    echo "  PASS: $desc"
    ((PASS++))
  else
    echo "  FAIL: $desc (pattern '$pattern' WAS found - should not be)"
    ((FAIL++))
  fi
}

echo "============================================"
echo "  MedVision AI Sprint 2 - Full API Tests"
echo "============================================"

# =============================================
# 1. HEALTH CHECK
# =============================================
echo ""
echo "=== 1. Health Check ==="
R=$(curl -s -w "\n%{http_code}" "$BASE/health")
CODE=$(echo "$R" | tail -1)
BODY=$(echo "$R" | head -1)
echo "  Response: $BODY"
check "Health returns 200" "200" "$CODE"
check_contains "status=healthy" '"status":"healthy"' "$BODY"
check_contains "database=healthy" '"database":"healthy"' "$BODY"

# =============================================
# 2. REGISTER USER
# =============================================
echo ""
echo "=== 2. Register User (201) ==="
R=$(curl -s -w "\n%{http_code}" -X POST "$BASE/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"dr.smith@example.com","password":"TestPass123!","full_name":"Dr. Jane Smith","role":"physician"}')
CODE=$(echo "$R" | tail -1)
BODY=$(echo "$R" | head -1)
echo "  Status: $CODE"
echo "  Body: $BODY"
if [[ "$CODE" == "201" ]]; then
  check "Register returns 201" "201" "$CODE"
else
  echo "  INFO: Got $CODE (user may already exist, trying with different email)"
  R=$(curl -s -w "\n%{http_code}" -X POST "$BASE/auth/register" \
    -H "Content-Type: application/json" \
    -d '{"email":"dr.jones@example.com","password":"TestPass123!","full_name":"Dr. Bob Jones","role":"researcher"}')
  CODE=$(echo "$R" | tail -1)
  BODY=$(echo "$R" | head -1)
  echo "  Status: $CODE  Body: $BODY"
  check "Register (new email) returns 201" "201" "$CODE"
fi
check_not_contains "password_hash NOT in response" "password_hash" "$BODY"
check_contains "email in response" '"email"' "$BODY"
check_contains "role in response" '"role"' "$BODY"

# =============================================
# 3. LOGIN
# =============================================
echo ""
echo "=== 3. Login (200) ==="
R=$(curl -s -w "\n%{http_code}" -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"dr.smith@example.com","password":"TestPass123!"}')
CODE=$(echo "$R" | tail -1)
BODY=$(echo "$R" | head -1)
echo "  Status: $CODE"
check "Login returns 200" "200" "$CODE"
check_contains "access_token present" '"access_token"' "$BODY"
check_contains "token_type=bearer" '"token_type":"bearer"' "$BODY"
check_contains "user object present" '"user"' "$BODY"

TOKEN=$(echo "$BODY" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['access_token'])" 2>/dev/null)
if [[ -z "$TOKEN" ]]; then
  echo "  FAIL: Could not extract token"
  ((FAIL++))
else
  echo "  Token extracted: ${TOKEN:0:40}..."
  ((PASS++))
fi

# =============================================
# 4. GET /me
# =============================================
echo ""
echo "=== 4. GET /auth/me (200) ==="
R=$(curl -s -w "\n%{http_code}" "$BASE/auth/me" \
  -H "Authorization: Bearer $TOKEN")
CODE=$(echo "$R" | tail -1)
BODY=$(echo "$R" | head -1)
echo "  Status: $CODE  Body: $BODY"
check "GET /me returns 200" "200" "$CODE"
check_contains "/me returns email" '"email"' "$BODY"
check_contains "/me returns role" '"role"' "$BODY"
check_not_contains "/me no password_hash" "password_hash" "$BODY"

# =============================================
# 5. CREATE STUDY
# =============================================
echo ""
echo "=== 5. POST /studies (201) ==="
R=$(curl -s -w "\n%{http_code}" -X POST "$BASE/studies" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "patient": {
      "mrn": "MRN001",
      "first_name": "John",
      "last_name": "Doe",
      "date_of_birth": "1980-05-15",
      "sex": "M"
    },
    "study": {
      "accession_number": "ACC001",
      "modality": "CT",
      "body_part": "CHEST",
      "study_description": "Chest CT with contrast",
      "study_date": "2024-01-15"
    }
  }')
CODE=$(echo "$R" | tail -1)
BODY=$(echo "$R" | head -1)
echo "  Status: $CODE"
echo "  Body: $BODY"
check "Create study returns 201" "201" "$CODE"
check_contains "modality=CT" '"modality":"CT"' "$BODY"
check_contains "patient embedded" '"patient"' "$BODY"
check_contains "status=created" '"status":"created"' "$BODY"

STUDY_ID=$(echo "$BODY" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['id'])" 2>/dev/null)
if [[ -z "$STUDY_ID" ]]; then
  echo "  FAIL: Could not extract study ID"
  ((FAIL++))
else
  echo "  Study ID: $STUDY_ID"
  ((PASS++))
fi

# =============================================
# 6. LIST STUDIES
# =============================================
echo ""
echo "=== 6. GET /studies (200) ==="
R=$(curl -s -w "\n%{http_code}" "$BASE/studies" \
  -H "Authorization: Bearer $TOKEN")
CODE=$(echo "$R" | tail -1)
BODY=$(echo "$R" | head -1)
echo "  Status: $CODE"
echo "  Body: $BODY"
check "List studies returns 200" "200" "$CODE"
check_contains "items array" '"items"' "$BODY"
check_contains "total count" '"total"' "$BODY"
check_contains "page field" '"page"' "$BODY"

# =============================================
# 7. GET STUDY DETAIL
# =============================================
echo ""
echo "=== 7. GET /studies/{id} (200) ==="
if [[ -n "$STUDY_ID" ]]; then
  R=$(curl -s -w "\n%{http_code}" "$BASE/studies/$STUDY_ID" \
    -H "Authorization: Bearer $TOKEN")
  CODE=$(echo "$R" | tail -1)
  BODY=$(echo "$R" | head -1)
  echo "  Status: $CODE"
  echo "  Body: $BODY"
  check "Get study detail returns 200" "200" "$CODE"
  check_contains "patient embedded" '"patient"' "$BODY"
  check_contains "modality present" '"modality"' "$BODY"
else
  echo "  SKIP: No study ID available"
fi

# =============================================
# 8. UPDATE STUDY
# =============================================
echo ""
echo "=== 8. PATCH /studies/{id} (200) ==="
if [[ -n "$STUDY_ID" ]]; then
  R=$(curl -s -w "\n%{http_code}" -X PATCH "$BASE/studies/$STUDY_ID" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"status":"ready","study_description":"Updated: Chest CT with contrast - completed"}')
  CODE=$(echo "$R" | tail -1)
  BODY=$(echo "$R" | head -1)
  echo "  Status: $CODE"
  echo "  Body: $BODY"
  check "Update study returns 200" "200" "$CODE"
  check_contains "status updated to ready" '"status":"ready"' "$BODY"
  check_contains "description updated" "Updated:" "$BODY"
else
  echo "  SKIP: No study ID available"
fi

# =============================================
# 9. ERROR CASES
# =============================================
echo ""
echo "=== 9. Error Cases ==="

# 9a: Duplicate email
echo "  --- 9a: Duplicate Email (409) ---"
R=$(curl -s -w "\n%{http_code}" -X POST "$BASE/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"dr.smith@example.com","password":"TestPass123!","full_name":"Dup User","role":"physician"}')
CODE=$(echo "$R" | tail -1)
echo "  Status: $CODE  Body: $(echo "$R" | head -1)"
check "Duplicate email returns 409" "409" "$CODE"

# 9b: Wrong password
echo "  --- 9b: Wrong Password (401) ---"
R=$(curl -s -w "\n%{http_code}" -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"dr.smith@example.com","password":"WrongPassword"}')
CODE=$(echo "$R" | tail -1)
echo "  Status: $CODE  Body: $(echo "$R" | head -1)"
check "Wrong password returns 401" "401" "$CODE"

# 9c: No token
echo "  --- 9c: No Token (401) ---"
R=$(curl -s -w "\n%{http_code}" "$BASE/auth/me")
CODE=$(echo "$R" | tail -1)
echo "  Status: $CODE  Body: $(echo "$R" | head -1)"
check "No token returns 401" "401" "$CODE"

# 9d: Fake study ID
echo "  --- 9d: Fake Study ID (404) ---"
R=$(curl -s -w "\n%{http_code}" "$BASE/studies/00000000-0000-0000-0000-000000000000" \
  -H "Authorization: Bearer $TOKEN")
CODE=$(echo "$R" | tail -1)
echo "  Status: $CODE  Body: $(echo "$R" | head -1)"
check "Fake study ID returns 404" "404" "$CODE"

# 9e: Weak password
echo "  --- 9e: Weak Password (422) ---"
R=$(curl -s -w "\n%{http_code}" -X POST "$BASE/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"new@example.com","password":"12345","full_name":"Weak User","role":"physician"}')
CODE=$(echo "$R" | tail -1)
echo "  Status: $CODE  Body: $(echo "$R" | head -1)"
check "Weak password returns 422" "422" "$CODE"

# =============================================
# SUMMARY
# =============================================
echo ""
echo "============================================"
echo "  RESULTS: $PASS passed, $FAIL failed"
echo "============================================"
if [[ $FAIL -eq 0 ]]; then
  echo "  ALL TESTS PASSED!"
else
  echo "  $FAIL TEST(S) FAILED"
fi
