# UI Testing Guide

This guide provides step-by-step instructions for manually testing all UI flows in the AI-Powered Recruitment Verification Platform.

## Prerequisites

1. Start the backend server:
   ```bash
   python app.py
   ```

2. Start the frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```

3. Open browser to `http://localhost:5173`

## Test Scenario 1: Create New Verification (Green Path)

### Steps:
1. Click "Create New Verification" button on home page
2. Fill in form:
   - Name: Sarah Chen
   - Email: sarah.chen@email.com
3. Click "Create Verification"
4. Verify success message appears
5. Copy the candidate portal URL
6. Verify redirect to verification list

### Expected Results:
- ✓ Form validates email format
- ✓ Loading spinner shows during submission
- ✓ Success message displays with portal URL
- ✓ New verification appears in list with "Pending Documents" status

## Test Scenario 2: Candidate Portal - Document Upload (Green)

### Steps:
1. Open candidate portal URL from previous test
2. Read welcome message
3. Upload CV (use `demo_scenarios/sample_documents/green_sarah_chen_cv.txt`)
4. Wait for processing
5. Read agent's response requesting paystub
6. Upload paystub document
7. Continue conversation until all documents collected
8. Review summary
9. Confirm accuracy

### Expected Results:
- ✓ Chat interface is responsive and smooth
- ✓ File upload shows progress indicator
- ✓ Agent asks relevant follow-up questions
- ✓ Document thumbnails/previews display
- ✓ No conflicts detected (green path)
- ✓ Summary is accurate
- ✓ Consent form displays
- ✓ Can sign electronically

## Test Scenario 3: Verification Progress Tracking

### Steps:
1. Return to verification list
2. Find Sarah Chen's verification
3. Click to view details
4. Observe real-time status updates
5. Watch progress bar advance
6. See timeline of completed activities

### Expected Results:
- ✓ Status updates automatically (polling works)
- ✓ Progress bar shows percentage
- ✓ Timeline shows: Document collection → Employment verification → References → GitHub analysis
- ✓ Each completed step has checkmark
- ✓ Smooth animations on updates

## Test Scenario 4: View Completed Report (Green)

### Steps:
1. Wait for verification to complete (or use pre-completed demo)
2. View verification detail page
3. Check risk score badge (should be GREEN)
4. Expand employment history section
5. Read verification status for each job
6. Expand technical validation section
7. Review GitHub analysis
8. Check red flags section (should be empty)
9. Read suggested interview questions
10. Click "Download PDF" button

### Expected Results:
- ✓ Risk score is prominently displayed in GREEN
- ✓ All sections expand/collapse smoothly
- ✓ Employment history shows verified status
- ✓ Reference quotes are displayed
- ✓ GitHub stats show charts/visualizations
- ✓ Code quality score displayed (8/10)
- ✓ No red flags section is empty or shows "No concerns"
- ✓ 5-10 interview questions generated
- ✓ PDF downloads successfully

## Test Scenario 5: Yellow Scenario - Employment Gap

### Steps:
1. Create new verification for Michael Rodriguez
2. Open candidate portal
3. Upload CV with employment gap
4. Upload available paystubs (only recent one)
5. Agent asks about employment gap
6. Respond: "I took time off for family care"
7. Agent asks for additional documentation
8. Respond: "I don't have formal documentation"
9. Complete document collection
10. View completed report

### Expected Results:
- ✓ Agent detects 15-month gap
- ✓ Conversational clarification is natural
- ✓ Agent records explanation
- ✓ Risk score is YELLOW
- ✓ Red flags section shows "Employment Gap" with MINOR severity
- ✓ Explanation is included in report
- ✓ Mixed reference feedback displayed
- ✓ GitHub shows corresponding activity gap

## Test Scenario 6: Red Scenario - Major Fraud Detection

### Steps:
1. Create new verification for David Thompson
2. Open candidate portal
3. Upload CV with inflated titles
4. Upload paystub showing different title
5. Agent detects conflict
6. Provide weak explanation
7. Upload diploma that doesn't match CV
8. Agent detects education fraud
9. Complete document collection
10. View completed report

### Expected Results:
- ✓ Agent immediately detects title mismatch
- ✓ Asks clarifying question about conflict
- ✓ Records conflicting information
- ✓ Detects education credential mismatch
- ✓ Risk score is RED
- ✓ Multiple CRITICAL fraud flags displayed
- ✓ Red flags section is prominent
- ✓ Report summary states "NOT RECOMMENDED FOR HIRE"
- ✓ Detailed evidence for each fraud flag
- ✓ GitHub analysis shows major skill mismatch

## Test Scenario 7: Search and Filter

### Steps:
1. Go to verification list page
2. Create multiple verifications (or use existing)
3. Use search box to search by name
4. Filter by status (Pending, In Progress, Completed)
5. Filter by risk score (Green, Yellow, Red)
6. Sort by date
7. Test pagination if many results

### Expected Results:
- ✓ Search filters results in real-time
- ✓ Status filter works correctly
- ✓ Risk score filter shows color-coded badges
- ✓ Sorting works properly
- ✓ Pagination displays correctly
- ✓ No results message shows when appropriate

## Test Scenario 8: Mobile Responsiveness

### Steps:
1. Open browser dev tools
2. Switch to mobile view (iPhone/Android)
3. Test all pages:
   - Verification list
   - Create verification form
   - Verification detail
   - Candidate portal
4. Test all interactions on mobile

### Expected Results:
- ✓ Layout adapts to mobile screen
- ✓ Navigation is accessible
- ✓ Forms are usable on mobile
- ✓ Chat interface works on mobile
- ✓ File upload works on mobile
- ✓ All buttons are tappable
- ✓ Text is readable without zooming

## Test Scenario 9: Error Handling

### Steps:
1. Try to create verification with invalid email
2. Try to upload unsupported file type
3. Try to upload file larger than 10MB
4. Disconnect internet and try to submit
5. Try to access non-existent verification ID
6. Try to submit form with missing fields

### Expected Results:
- ✓ Email validation shows error message
- ✓ File type validation prevents upload
- ✓ File size validation shows error
- ✓ Network error shows user-friendly message
- ✓ 404 page shows for invalid IDs
- ✓ Required field validation works
- ✓ All error messages are clear and helpful

## Test Scenario 10: Animations and Polish

### Steps:
1. Navigate between pages
2. Expand/collapse sections
3. Hover over buttons and cards
4. Watch loading states
5. Observe status transitions
6. Test smooth scrolling

### Expected Results:
- ✓ Page transitions are smooth
- ✓ Section expand/collapse animates nicely
- ✓ Hover effects are subtle and professional
- ✓ Loading spinners are smooth
- ✓ Status changes animate
- ✓ Scrolling is smooth
- ✓ No janky animations
- ✓ Consistent timing across all animations

## Performance Checklist

- [ ] Pages load in under 2 seconds
- [ ] No layout shift during load
- [ ] Images load progressively
- [ ] Smooth 60fps animations
- [ ] No memory leaks during navigation
- [ ] API calls are debounced appropriately
- [ ] Large lists are virtualized if needed

## Accessibility Checklist

- [ ] All interactive elements are keyboard accessible
- [ ] Tab order is logical
- [ ] Focus indicators are visible
- [ ] Color contrast meets WCAG AA standards
- [ ] Screen reader can navigate properly
- [ ] Form labels are associated correctly
- [ ] Error messages are announced
- [ ] Loading states are announced

## Browser Compatibility

Test in:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS)
- [ ] Mobile Chrome (Android)

## Sign-Off

After completing all test scenarios:

- [ ] All UI flows work correctly
- [ ] No critical bugs found
- [ ] Performance is acceptable
- [ ] Accessibility requirements met
- [ ] Mobile experience is good
- [ ] Error handling is robust
- [ ] Animations are polished

**Tester Name:** _______________
**Date:** _______________
**Notes:** _______________
