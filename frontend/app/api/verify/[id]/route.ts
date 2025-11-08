import { NextRequest, NextResponse } from 'next/server';
import { getVerification } from '@/lib/supabase';

export async function GET(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;

    if (!id) {
      return NextResponse.json(
        { error: 'Verification ID is required' },
        { status: 400 }
      );
    }

    // Fetch verification from Supabase
    const verification = await getVerification(id);

    if (!verification) {
      return NextResponse.json(
        { error: 'Verification not found' },
        { status: 404 }
      );
    }

    return NextResponse.json(verification);

  } catch (error) {
    console.error('API error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch verification' },
      { status: 500 }
    );
  }
}
