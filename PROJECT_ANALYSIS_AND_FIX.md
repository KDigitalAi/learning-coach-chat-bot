# Complete Project Analysis & 404 Fix

## 1. Project Structure Analysis

### Project Type: **Monorepo (Frontend + Backend)**

**Frontend:**
- Static HTML/CSS/JS files in root directory
- `index.html` - Main HTML file
- `script.js` - Frontend JavaScript (903+ lines)
- `style.css` - Styles
- **No build process** - Files are served as-is
- **No build output directory** - Files are in root

**Backend:**
- Python FastAPI application in `backend/app/`
- Serverless function wrapper in `api/index.py`
- Uses Mangum to adapt FastAPI to Vercel's Lambda format

**API Routes:**
- `/api/chat` - Main chat endpoint
- `/api/onboarding/consent` - Onboarding endpoint
- `/health` - Health check
- `/` - API root (conflicts with frontend!)

---

## 2. Root Cause of 404 Error

### Primary Issues:

1. **Legacy `builds` Configuration**
   - Using deprecated `builds` section overrides Vercel's auto-detection
   - Causes warning and potential routing issues
   - Doesn't properly handle static file serving

2. **Route Ordering Problem**
   - Current routes have API routes first (good)
   - But catch-all `/(.*)` might be interfering
   - The root `/` route in FastAPI conflicts with frontend `index.html`

3. **Static File Serving**
   - With `builds` config, Vercel doesn't automatically serve root-level static files
   - Need explicit configuration for static assets

4. **Missing Frontend Build Output**
   - No `dist/` or `build/` directory
   - Files are in root, which should work but needs proper config

---

## 3. Why `builds` Overrides Vercel Settings

When `builds` exists in `vercel.json`:
- Vercel **ignores** Project Settings from dashboard
- Only uses what's in `vercel.json`
- Requires explicit configuration for everything
- Can cause static files to not be served automatically

**Solution:** Remove `builds` and use modern auto-detection + `rewrites`

---

## 4. Corrected Configuration

### Fixed `vercel.json`:

```json
{
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/api/index"
    },
    {
      "source": "/health",
      "destination": "/api/index"
    }
  ],
  "routes": [
    {
      "src": "/(.*\\.(js|css|png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf|eot))",
      "dest": "/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

**Key Changes:**
1. ✅ Removed `builds` - Use auto-detection
2. ✅ Added `rewrites` for API routes (modern approach)
3. ✅ Static assets route first (before catch-all)
4. ✅ Catch-all routes to `index.html` for SPA

---

## 5. File Edits Required

### Edit 1: `vercel.json` (Complete Replacement)

