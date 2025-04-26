# Conversation Transcript: Marketing Site Configuration Fix

## Initial Problem
The marketing site had configuration issues with Next.js that were preventing it from starting properly.

## Changes Made
1. Fixed next.config.js by removing deprecated options:
   - Removed `swcMinify: true` option which is no longer needed in modern Next.js
   - Removed the deprecated `jsx: true` option from the compiler settings
   - Updated other configuration options to be compatible with the latest Next.js version

2. The fix resolved the warnings:
   ```
   ⚠ Invalid next.config.js options detected: 
   ⚠ Unrecognized key(s) in object: 'jsx' at "compiler"
   ⚠ Unrecognized key(s) in object: 'swcMinify'
   ```

3. Successfully started the Marketing Site Alternative workflow on port 5050

## Results
The marketing site now starts up without configuration warnings and displays correctly.

## Key Files Modified
- apps/marketing/next.config.js

## Next Steps
The marketing site is now running successfully. There are some other errors in the console logs related to the dashboard components and API calls (404 errors for some trpc routes), but these are related to the main application rather than the marketing site that was fixed.