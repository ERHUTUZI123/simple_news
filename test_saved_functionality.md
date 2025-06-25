# Saved Page Functionality Test Guide

## Test Environment
- Frontend: http://localhost:5175
- Backend: http://localhost:8000

## Function Test Steps

### 1. Save Article Test
1. Visit homepage http://localhost:5175
2. Find any news card
3. Click "⭐ Save" button
4. Verify button status changes to "⭐ Saved"
5. Click "Saved" in navigation bar to enter saved page
6. Verify article appears in saved list

### 2. Saved Page Function Test
1. Check saved count display on saved page
2. Click "📖 Read Summary" to jump to article detail page
3. Click "🔗 View Original" to open original article in new tab
4. Click "🗑️ Remove" to delete article
5. Verify Toast notification shows "Removed from saved"
6. Click "Undo" button in Toast to restore article
7. Verify article reappears in saved list

### 3. Export Function Test
1. Ensure there are articles on saved page
2. Click "📂 Export All (.md)" button
3. Verify file download (saved-articles-YYYY-MM-DD.md)
4. Click "📄 Export as TXT" button
5. Verify file download (saved-articles-YYYY-MM-DD.txt)
6. Check if exported file content format is correct

### 4. State Synchronization Test
1. Save an article on homepage
2. Click "📖 Read Summary" to enter article detail page
3. Verify saved status shows as saved
4. Cancel save on article detail page
5. Return to homepage and verify saved status updated
6. Enter saved page and verify article removed

### 5. Empty State Test
1. Clear all saved articles (remove all articles)
2. Enter saved page
3. Verify empty state prompt displayed
4. Verify export buttons not displayed
5. Verify saved count shows 0

### 6. Responsive Test
1. Test on mobile device or browser developer tools
2. Verify saved page display effect on mobile
3. Verify button arrangement on small screen
4. Verify Toast notification position on mobile

## Expected Results

### Save Function
- ✅ Save status synchronized across all pages
- ✅ Save data persisted to localStorage
- ✅ Save button status correctly toggled

### Saved Page Function
- ✅ Correctly display saved count
- ✅ Saved list correctly rendered
- ✅ Remove save function normal
- ✅ Undo function normal
- ✅ Toast notification correctly displayed

### Export Function
- ✅ Markdown format export correct
- ✅ TXT format export correct
- ✅ Filename contains date
- ✅ File content format correct

### User Experience
- ✅ Smooth animation effects
- ✅ Responsive design adaptation
- ✅ Friendly empty state prompt
- ✅ Timely operation feedback

## Technical Verification

### localStorage Data
```javascript
// Check in browser console
localStorage.getItem('savedArticles')
```

### Data Format
```json
[
  {
    "title": "Article Title",
    "link": "Original Link",
    "date": "Publish Time",
    "source": "Source",
    "content": "Article Content",
    "summary": "AI Summary"
  }
]
```

## Common Issues

### 1. Save Status Not Synchronized
- Check if localStorage data correctly saved
- Check if useEffect dependencies correct

### 2. Export Function Not Working
- Check if browser supports Blob API
- Check file download permissions

### 3. Animation Effects Not Displaying
- Check if CSS animations correctly loaded
- Check if browser supports CSS animations

### 4. Mobile Display Issues
- Check if CSS media queries correct
- Check viewport settings 