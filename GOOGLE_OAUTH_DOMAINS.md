# Google OAuth Domain Configuration

## 🔧 Based on Your Screenshot

Your current configuration is mostly correct! Here are the exact domains you should add:

### **Authorized JavaScript Origins**
Add these URLs (click "ADD URI" for each):

```
https://resumee-khaki.vercel.app        ✅ (already added)
http://localhost:3000                   ➕ (add this for local development)
https://localhost:3000                  ➕ (add this for HTTPS local)
```

### **Authorized Redirect URIs**
Add these URLs (click "ADD URI" for each):

```
https://resumee-khaki.vercel.app        ✅ (already added)  
http://localhost:3000                   ➕ (add this for local development)
https://localhost:3000                  ➕ (add this for HTTPS local)
```

## 📋 Step-by-Step Instructions

1. **Click "ADD URI" under "Authorized JavaScript origins"**
2. **Add**: `http://localhost:3000`
3. **Click "ADD URI" again**
4. **Add**: `https://localhost:3000`

5. **Click "ADD URI" under "Authorized redirect URIs"**
6. **Add**: `http://localhost:3000`
7. **Click "ADD URI" again**
8. **Add**: `https://localhost:3000`

9. **Click "SAVE" at the bottom**

## 🔑 Copy Your Client ID

From your screenshot, copy the **Client ID** (the long string that ends with `.googleusercontent.com`)

## 📝 Update Your Environment Files

### **Production (Vercel)**
Set environment variable:
```
REACT_APP_GOOGLE_CLIENT_ID=your_client_id_from_screenshot.googleusercontent.com
```

### **Local Development**
Update `tailorcv-frontend/.env`:
```bash
REACT_APP_GOOGLE_CLIENT_ID=your_client_id_from_screenshot.googleusercontent.com
REACT_APP_API_URL=http://localhost:5000
```

Update `tailorcv-backend/.env`:
```bash
GOOGLE_CLIENT_ID=your_client_id_from_screenshot.googleusercontent.com
JWT_SECRET=your_secure_random_key_here
```

## ✅ Your Configuration Will Work!

The setup you have is almost perfect. Just add the localhost domains for development testing, and you'll be all set!

## 🚀 Testing Steps

1. **Save the Google Cloud Console changes**
2. **Copy your Client ID to the environment files**
3. **Restart your applications**
4. **Test both**:
   - Local: http://localhost:3000
   - Production: https://resumee-khaki.vercel.app

Both should now work with Google OAuth!