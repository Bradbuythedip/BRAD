# BRAD Website Deployment

The website is ready to deploy on GitHub Pages.

---

## Quick Setup (GitHub Pages)

### Step 1: Enable GitHub Pages

1. Go to your repository: https://github.com/Bradbuythedip/BRAD
2. Click **Settings** (top right)
3. Scroll down to **Pages** (left sidebar)
4. Under "Build and deployment":
   - **Source**: Deploy from a branch
   - **Branch**: main
   - **Folder**: `/` (root)
5. Click **Save**

### Step 2: Wait for Deployment

GitHub will automatically build and deploy your site. This takes 1-2 minutes.

You'll see a message: "Your site is live at https://bradbuythedip.github.io/BRAD/"

### Step 3: Access Your Website

Your website will be available at:
**https://bradbuythedip.github.io/BRAD/web/**

Or set it to root by moving index.html:
```bash
cd ~/brad
mv web/index.html index.html
git add index.html
git commit -m "Move website to root"
git push
```

Then it will be at: **https://bradbuythedip.github.io/BRAD/**

---

## Custom Domain (Optional)

### Step 1: Buy Domain

Buy a domain like `bradloop.ai` from:
- Namecheap
- Google Domains
- Cloudflare

### Step 2: Configure DNS

Add these DNS records at your domain registrar:

```
Type: A
Name: @
Value: 185.199.108.153

Type: A
Name: @
Value: 185.199.109.153

Type: A
Name: @
Value: 185.199.110.153

Type: A
Name: @
Value: 185.199.111.153

Type: CNAME
Name: www
Value: bradbuythedip.github.io
```

### Step 3: Configure GitHub

1. Go to Settings → Pages
2. Under "Custom domain", enter: `bradloop.ai`
3. Click Save
4. Wait for DNS check (can take up to 24 hours)
5. Enable "Enforce HTTPS"

---

## Website Features

### Current Page Includes:

✅ **Hero Section**
- BRAD logo and tagline
- Call-to-action buttons
- Gradient styling with brand colors

✅ **Metrics Display**
- Hofstadter Index: 0.0-1.0
- Cognitive Levels: 3
- Strange Loops: ∞
- Dependencies: 0

✅ **About Section**
- Core thesis
- What is BRAD
- Hofstadter quote

✅ **Architecture**
- 3-level hierarchy diagram
- Code example
- Interactive sections

✅ **Features Grid**
- Strange Loops
- Self-Reference
- Quantifiable Consciousness
- Gödelian Limits
- Twitter Bot
- Lightweight

✅ **Token Information**
- $BRAD details
- Governance
- Launch info
- Link to tokenomics

✅ **Gödelian Blind Spots**
- Consistency (Gödel)
- Halting (Turing)
- Qualia (Chalmers)

✅ **Get Started**
- Installation code
- Links to docs
- GitHub integration

✅ **Footer**
- Social links
- Hofstadter quote
- License info

### Styling:

- **Colors**: Cyan (#00D4AA), Pink (#FF6B9D), Gold (#FFC759)
- **Typography**: System fonts for speed
- **Responsive**: Mobile-friendly
- **Dark theme**: Matches crypto/tech aesthetic
- **Animations**: Hover effects, gradients

---

## Local Testing

Before deploying, test locally:

```bash
cd ~/brad/web

# Python 3
python3 -m http.server 8000

# Or Python 2
python -m SimpleHTTPServer 8000

# Or Node.js
npx http-server -p 8000
```

Then open: http://localhost:8000/index.html

---

## Alternative Hosting Options

### Netlify (Easiest)

1. Go to https://netlify.com
2. Connect GitHub account
3. Import repository: Bradbuythedip/BRAD
4. Build settings:
   - Base directory: `web`
   - Publish directory: `.`
5. Deploy
6. Free custom domain: `brad.netlify.app`

### Vercel

1. Go to https://vercel.com
2. Import GitHub repo
3. Configure:
   - Root directory: `web`
4. Deploy
5. Free custom domain: `brad.vercel.app`

### Cloudflare Pages

1. Go to https://pages.cloudflare.com
2. Connect GitHub
3. Select repo
4. Build settings:
   - Build output directory: `web`
5. Deploy

---

## Website Updates

To update the website:

```bash
cd ~/brad

# Edit website
nano web/index.html

# Commit and push
git add web/
git commit -m "Update website"
git push

# GitHub Pages will auto-rebuild (1-2 min)
```

---

## Adding More Pages

Create additional pages in `web/`:

```bash
cd ~/brad/web

# Create docs page
cat > docs.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>BRAD - Documentation</title>
    <link rel="stylesheet" href="index.html">
</head>
<body>
    <h1>Documentation</h1>
    <!-- Content here -->
</body>
</html>
EOF

git add web/docs.html
git commit -m "Add docs page"
git push
```

---

## SEO Optimization

The website already includes:

✅ Meta tags (title, description, keywords)
✅ Open Graph tags (for social sharing)
✅ Twitter Card tags
✅ Semantic HTML
✅ Fast loading (no external dependencies)
✅ Mobile responsive

To improve further:

1. **Add sitemap.xml**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://bradbuythedip.github.io/BRAD/</loc>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
```

2. **Submit to Google**: https://search.google.com/search-console
3. **Add analytics** (optional):
```html
<!-- Add before </head> -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
```

---

## Maintenance

### Check Website Status

```bash
# Test if site is up
curl -I https://bradbuythedip.github.io/BRAD/web/

# Should return: HTTP/2 200
```

### Monitor Performance

Use these tools:
- Google PageSpeed Insights
- GTmetrix
- WebPageTest

Current performance:
- Load time: <1 second
- No external dependencies
- Lightweight (~20KB HTML)

---

## Troubleshooting

### "404 - File not found"

**Problem**: GitHub Pages can't find the file.

**Solution**: 
- Ensure `web/index.html` exists in main branch
- Check GitHub Pages settings point to correct folder
- Wait 1-2 minutes for rebuild

### "Site not updating"

**Problem**: Changes not appearing.

**Solution**:
```bash
# Force clear cache
git commit --allow-empty -m "Trigger rebuild"
git push

# Or clear browser cache
Ctrl+Shift+R (hard refresh)
```

### Custom domain not working

**Problem**: Domain shows error.

**Solution**:
- DNS changes take up to 24 hours
- Check DNS propagation: https://dnschecker.org/
- Ensure CNAME file exists in repo
- Verify GitHub Pages settings

---

## Summary

✅ **Website created**: `web/index.html`
✅ **Ready to deploy**: GitHub Pages
✅ **URL**: https://bradbuythedip.github.io/BRAD/web/
✅ **Features**: Full landing page with all sections
✅ **Responsive**: Mobile-friendly
✅ **Fast**: No external dependencies
✅ **SEO**: Meta tags included

**Next step**: Enable GitHub Pages in repository settings!

---

*Built with 🧠 and ♾️*
