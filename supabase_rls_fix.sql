-- Allow anonymous users to read verification_steps table
-- This enables the frontend to fetch progress updates

-- For verification_steps table
ALTER TABLE verification_steps ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow anonymous read access to verification_steps"
ON verification_steps
FOR SELECT
TO anon
USING (true);

-- For verifications table (if needed)
ALTER TABLE verifications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow anonymous read access to verifications"
ON verifications
FOR SELECT
TO anon
USING (true);
