'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to dashboard
    router.push('/dashboard');
  }, [router]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0a0f] via-[#0f0f1a] to-[#0a0a0f] flex items-center justify-center p-8">
      <div className="text-center">
        <Loader2 className="animate-spin h-16 w-16 text-purple-500 mx-auto mb-4" />
        <p className="text-[#9ca3af] text-lg">Redirecting to dashboard...</p>
      </div>
    </div>
  );
}
