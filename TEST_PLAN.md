# Test Plan - Blast Radius

## 🧪 Testing Strategy

This document outlines how to test the Blast Radius application to ensure all features work correctly for the hackathon demo.

---

## 📋 Test Cases

### 1. Repository Cloning & Ingestion

#### Test Case 1.1: Local Repository Path
- **Input**: `/path/to/local/repo` (e.g., the Arka repository itself)
- **Expected**: Repository is parsed successfully
- **Steps**:
  1. Enter local path in the input field
  2. Press Enter or click submit
  3. Verify repository overview loads
  4. Verify files are scanned and parsed
- **Status**: ✅ Should work

#### Test Case 1.2: GitHub HTTPS URL
- **Input**: `https://github.com/CodeManBist/Arka`
- **Expected**: Repository is cloned to temp dir, parsed, then cleaned up
- **Steps**:
  1. Enter GitHub URL in the input field
  2. Press Enter or click submit
  3. Verify repository is cloned (check temp directory)
  4. Verify repository overview loads
  5. Verify temp directory is cleaned up after analysis
- **Status**: ✅ NEW - Should work with repository_manager

#### Test Case 1.3: GitHub SSH URL
- **Input**: `git@github.com:CodeManBist/Arka.git`
- **Expected**: Repository is cloned and parsed
- **Steps**: Same as 1.2
- **Status**: ✅ NEW - Should work with repository_manager

#### Test Case 1.4: Invalid Repository Path
- **Input**: `/path/that/does/not/exist`
- **Expected**: Clear error message: "Local path does not exist"
- **Status**: ✅ Should work

#### Test Case 1.5: Invalid GitHub URL
- **Input**: `https://github.com/nonexistent/repo`
- **Expected**: Clear error message: "Failed to clone repository"
- **Status**: ✅ Should work

### 2. Repository Overview

#### Test Case 2.1: Overview Statistics
- **Input**: Valid repository
- **Expected**: 
  - Repository name displayed
  - Total files count
  - Language breakdown
  - Symbol counts (functions, classes, imports, exports)
  - Call graph stats
  - Import graph stats
  - Critical services list
- **Status**: ✅ Should work

#### Test Case 2.2: Multiple Languages
- **Input**: Repository with Python, JavaScript, TypeScript files
- **Expected**: All languages detected and displayed
- **Status**: ✅ Should work

### 3. Symbol Analysis

#### Test Case 3.1: Analyze Function
- **Input**: 
  - Repository: Valid repo
  - Symbol: `processPayment` (or any function name)
  - Type: function
- **Expected**: 
  - Impact result with:
    - Direct callers count
    - Transitive callers count
    - Affected files list
    - Risk level and score
    - Confidence score
    - AI summary
    - Suggested fix
- **Status**: ✅ Should work

#### Test Case 3.2: Analyze Class
- **Input**: 
  - Repository: Valid repo
  - Symbol: `PaymentService` (or any class name)
  - Type: class
- **Expected**: Same as 3.1 but for class
- **Status**: ✅ Should work

#### Test Case 3.3: Non-existent Symbol
- **Input**: 
  - Repository: Valid repo
  - Symbol: `nonExistentFunction123`
- **Expected**: Error message or low confidence result
- **Status**: ✅ Should work

### 4. Diff Analysis

#### Test Case 4.1: Simple Diff
- **Input**: 
  ```diff
  diff --git a/src/payments.py b/src/payments.py
  index abc123..def456 100644
  --- a/src/payments.py
  +++ b/src/payments.py
  @@ -10,7 +10,7 @@ class PaymentService:
   @app.route('/process', methods=['POST'])
  -def process_payment(user):
  +def process_payment(user, currency):
      # Process payment logic
      amount = calculate_amount(user)
      return charge_user(user, amount)
  ```
- **Expected**: 
  - Changed symbol detected: `process_payment`
  - Impact analysis for the changed function
  - Summary with risk level, confidence, etc.
- **Status**: ✅ Should work

#### Test Case 4.2: Multiple Changes
- **Input**: Diff with multiple function changes
- **Expected**: 
  - All changed symbols detected
  - Impact analysis for each
  - Aggregated summary
- **Status**: ✅ Should work

#### Test Case 4.3: Empty Diff
- **Input**: Empty string or no changes
- **Expected**: Message: "No changed symbols detected"
- **Status**: ✅ Should work

### 5. PR Comment Generation

#### Test Case 5.1: Generate Comment
- **Input**: Valid diff
- **Expected**: 
  - Formatted PR comment with:
    - Header
    - Risk level and confidence
    - Summary statistics
    - Changed symbols list
    - Individual analyses
    - Suggested actions
    - Footer with link
- **Status**: ✅ Should work

#### Test Case 5.2: Copy to Clipboard
- **Input**: Generated PR comment
- **Action**: Click "Copy to Clipboard" button
- **Expected**: 
  - Comment copied to clipboard
  - Success message displayed
- **Status**: ✅ Should work

### 6. Graph Visualization

#### Test Case 6.1: Display Graph
- **Input**: Valid impact result or diff analysis
- **Expected**: 
  - Interactive graph displayed
  - Changed symbol highlighted
  - Nodes color-coded by risk level
  - Clickable nodes with details
  - Zoom and pan functionality
- **Status**: ✅ NEW - Should work with D3.js component

#### Test Case 6.2: Blast Radius Animation
- **Input**: Valid graph
- **Action**: Click "Animate Blast Radius"
- **Expected**: 
  - Nodes pulse outward from changed symbol
  - Smooth animation
- **Status**: ✅ NEW - Should work

#### Test Case 6.3: Node Details
- **Input**: Valid graph
- **Action**: Click on a node
- **Expected**: 
  - Tooltip displayed with node details
  - Name, type, file path, risk level
- **Status**: ✅ NEW - Should work

### 7. Error Handling

#### Test Case 7.1: Network Error
- **Action**: Disable network, try to analyze
- **Expected**: Clear error message
- **Status**: ✅ Should work

#### Test Case 7.2: Invalid API Response
- **Action**: Mock invalid response from backend
- **Expected**: Error message displayed
- **Status**: ✅ Should work

#### Test Case 7.3: Parsing Error
- **Input**: Repository with syntax errors
- **Expected**: Error message about parsing failure
- **Status**: ✅ Should work

### 8. UI/UX

#### Test Case 8.1: Dark Mode
- **Expected**: 
  - Dark background
  - Light text
  - Proper contrast
  - No white flashes
- **Status**: ✅ Should work

#### Test Case 8.2: Loading States
- **Action**: Trigger any async operation
- **Expected**: 
  - Loading spinner displayed
  - Buttons disabled during loading
  - Skeleton loaders for content
- **Status**: ✅ NEW - Should work

#### Test Case 8.3: Error States
- **Action**: Trigger an error
- **Expected**: 
  - Error alert displayed
  - Clear error message
  - Dismiss button works
- **Status**: ✅ NEW - Should work

#### Test Case 8.4: Success States
- **Action**: Complete a successful operation
- **Expected**: 
  - Success alert displayed
  - Clear success message
  - Dismiss button works
- **Status**: ✅ NEW - Should work

#### Test Case 8.5: Responsive Design
- **Action**: Resize browser window
- **Expected**: 
  - Layout adapts to screen size
  - No overflow issues
  - Mobile-friendly on small screens
- **Status**: ✅ Should work

#### Test Case 8.6: Animations
- **Action**: Hover over buttons, switch tabs
- **Expected**: 
  - Smooth transitions
  - Hover effects
  - Tab switching animations
- **Status**: ✅ NEW - Should work

---

## 🏃 Running the Tests

### Manual Testing

1. **Start all services**:
   ```bash
   docker-compose up --build
   ```
   
   Or manually:
   ```bash
   # AI Service
   cd ai-service
   pip install -r requirements.txt
   uvicorn app:app --reload --port 8000
   
   # Backend
   cd backend
   npm install
   npm run dev
   
   # Frontend
   cd frontend
   npm install
   npm run dev
   ```

2. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend: http://localhost:4000
   - AI Service: http://localhost:8000

3. **Run through the demo script**:
   - Follow the 3-minute demo script from the README
   - Test each feature as described above

### Automated Testing

#### Backend Tests
```bash
cd ai-service
python -m pytest tests/ -v
```

#### API Tests
```bash
# Test health endpoints
curl http://localhost:8000/
curl http://localhost:4000/

# Test repository overview
curl -X POST http://localhost:8000/api/blast-radius/repository-overview \
  -H "Content-Type: application/json" \
  -d '{"repository_path": "/path/to/repo"}'

# Test symbol analysis
curl -X POST http://localhost:8000/api/blast-radius/analyze \
  -H "Content-Type: application/json" \
  -d '{"repository_path": "/path/to/repo", "symbol_name": "main", "symbol_type": "function"}'
```

---

## 📊 Test Results Template

| Test Case | Description | Expected | Actual | Status | Notes |
|-----------|-------------|----------|--------|--------|-------|
| 1.1 | Local path | Success | | | | |
| 1.2 | GitHub HTTPS | Success | | | | |
| 1.3 | GitHub SSH | Success | | | | |
| 1.4 | Invalid path | Error | | | | |
| 1.5 | Invalid URL | Error | | | | |
| 2.1 | Overview stats | All stats | | | | |
| 3.1 | Analyze function | Impact result | | | | |
| 4.1 | Simple diff | Analysis | | | | |
| 5.1 | Generate comment | PR comment | | | | |
| 6.1 | Display graph | Interactive | | | | |
| 7.1 | Network error | Error message | | | | |
| 8.1 | Dark mode | Dark UI | | | | |

---

## 🎯 Critical Path Testing

For the hackathon demo, focus on these critical tests:

1. ✅ **GitHub URL cloning** - Must work for demo
2. ✅ **Repository overview** - Must show stats
3. ✅ **Diff analysis** - Must detect changes
4. ✅ **PR comment generation** - Must generate comment
5. ✅ **Graph visualization** - Must show graph (even text representation)

---

## 🐛 Known Issues & Workarounds

### Issue 1: Tree-sitter Parsers Not Installed
- **Symptom**: Parsing fails with "Language not found"
- **Workaround**: Install tree-sitter parsers:
  ```bash
  pip install tree-sitter-python tree-sitter-javascript tree-sitter-typescript
  ```

### Issue 2: GitHub Rate Limiting
- **Symptom**: Clone fails with rate limit error
- **Workaround**: 
  - Use GitHub token: Set `GITHUB_TOKEN` environment variable
  - Or use local repositories for testing

### Issue 3: Large Repositories
- **Symptom**: Slow parsing for large repos
- **Workaround**: Use small repositories for testing

### Issue 4: Missing Dependencies
- **Symptom**: Import errors
- **Workaround**: Run `pip install -r requirements.txt`

---

## 📝 Test Notes

### Pre-Test Checklist
- [ ] All services running
- [ ] Dependencies installed
- [ ] Tree-sitter parsers installed
- [ ] GitHub token configured (optional)
- [ ] Test repositories available

### Post-Test Checklist
- [ ] All critical features working
- [ ] Error handling verified
- [ ] UI/UX polished
- [ ] Performance acceptable
- [ ] Ready for demo

---

## 🏆 Sign-Off

**Tester**: ___________________
**Date**: ___________________
**Status**: ✅ Ready for Hackathon Demo

**Notes**:
________________________________________________________
