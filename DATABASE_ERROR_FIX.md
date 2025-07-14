# 🔧 Fix Database "Column Does Not Exist" Error

## 🚨 Error: `column "user_id" does not exist`

This error occurs because your existing database tables don't have the required columns for Google OAuth authentication.

## ✅ Quick Fix - Run This SQL Script

### Step 1: Go to Supabase SQL Editor
1. **Open your Supabase project**
2. **Click "SQL Editor"** in the left sidebar
3. **Click "New Query"**

### Step 2: Copy and Run the Fix Script
Copy the **entire content** from `fix_database_schema.sql` and paste it into the SQL editor, then click **"RUN"**.

**Or copy this simplified version:**

```sql
-- Quick fix for column errors
DO $$ 
BEGIN
    -- Add user_id to generations table if it doesn't exist
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='generations') THEN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='generations' AND column_name='user_id') THEN
            ALTER TABLE generations ADD COLUMN user_id UUID;
        END IF;
    END IF;

    -- Add user_id to payments table if it doesn't exist  
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='payments') THEN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='payments' AND column_name='user_id') THEN
            ALTER TABLE payments ADD COLUMN user_id UUID;
        END IF;
    END IF;

    -- Create users table if it doesn't exist
    CREATE TABLE IF NOT EXISTS users (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        email TEXT UNIQUE,
        google_id TEXT UNIQUE,
        name TEXT,
        profile_picture TEXT,
        google_email TEXT,
        last_login TIMESTAMP WITH TIME ZONE,
        auth_provider TEXT DEFAULT 'google',
        ip TEXT,
        is_premium BOOLEAN DEFAULT FALSE,
        generation_count INTEGER DEFAULT 0,
        last_generated TIMESTAMP WITH TIME ZONE,
        upgraded_at TIMESTAMP WITH TIME ZONE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Create user_sessions table
    CREATE TABLE IF NOT EXISTS user_sessions (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        session_token TEXT NOT NULL UNIQUE,
        expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Create user_preferences table
    CREATE TABLE IF NOT EXISTS user_preferences (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        theme TEXT DEFAULT 'light',
        email_notifications BOOLEAN DEFAULT TRUE,
        preferred_template TEXT DEFAULT 'professional',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
END $$;

-- Add foreign key constraints if they don't exist
DO $$
BEGIN
    -- Add foreign key to generations table
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'generations_user_id_fkey'
    ) THEN
        ALTER TABLE generations ADD CONSTRAINT generations_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES users(id);
    END IF;

    -- Add foreign key to payments table  
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'payments_user_id_fkey'
    ) THEN
        ALTER TABLE payments ADD CONSTRAINT payments_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES users(id);
    END IF;
END $$;

SELECT 'Database fixed! Column errors should be resolved.' AS result;
```

### Step 3: Verify the Fix
After running the script, you should see:
```
Database fixed! Column errors should be resolved.
```

## 🔍 What This Script Does

1. **Safely adds missing columns** to existing tables
2. **Creates required tables** if they don't exist
3. **Adds proper foreign key relationships**
4. **Won't break existing data** - uses `IF NOT EXISTS` checks

## 🚀 After Running the Script

1. **Restart your backend**: `cd tailorcv-backend && python app.py`
2. **Test Google OAuth** again
3. **Should now work without column errors**

## 📋 If You Still Get Errors

### Check Your Tables Exist
Run this in Supabase SQL Editor:
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

Should show:
- `generations`
- `payments` 
- `users`
- `user_sessions`
- `user_preferences`

### Check Columns Exist
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'generations' 
ORDER BY column_name;
```

Should include `user_id` column.

## ✅ Expected Result

After running this fix:
- ✅ No more "column does not exist" errors
- ✅ Google OAuth authentication works
- ✅ Users can sign in and their data gets saved properly
- ✅ All database relationships work correctly

The main issue was that your existing database was missing the columns needed for user authentication. This script adds them safely without breaking existing data!