-- Fix RLS policies for verification_steps table
-- This allows the frontend (using anon key) to read verification steps

-- Drop existing policies if any
DROP POLICY IF EXISTS "Allow anonymous read access to verification_steps" ON verification_steps;
DROP POLICY IF EXISTS "Allow service role full access to verification_steps" ON verification_steps;

-- Enable RLS on verification_steps table
ALTER TABLE verification_steps ENABLE ROW LEVEL SECURITY;

-- Allow anonymous users to read verification steps
CREATE POLICY "Allow anonymous read access to verification_steps"
ON verification_steps
FOR SELECT
TO anon
USING (true);

-- Allow service role full access (for backend operations)
CREATE POLICY "Allow service role full access to verification_steps"
ON verification_steps
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- Also verify the verifications table has proper policies
DROP POLICY IF EXISTS "Allow anonymous read access to verifications" ON verifications;
DROP POLICY IF EXISTS "Allow service role full access to verifications" ON verifications;

ALTER TABLE verifications ENABLE ROW LEVEL SECURITY;

-- Allow anonymous users to read verifications
CREATE POLICY "Allow anonymous read access to verifications"
ON verifications
FOR SELECT
TO anon
USING (true);

-- Allow service role full access to verifications
CREATE POLICY "Allow service role full access to verifications"
ON verifications
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);
