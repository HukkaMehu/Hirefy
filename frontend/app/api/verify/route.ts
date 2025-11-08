import { NextRequest, NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    
    const {
      candidateName,
      candidateEmail,
      candidatePhone,
      candidateLinkedIn,
      company,
      position,
      startDate,
      endDate,
      verificationOptions,
    } = body;

    // Validate required fields
    if (!candidateName || !candidateEmail || !candidatePhone) {
      return NextResponse.json(
        { error: 'Missing required candidate information' },
        { status: 400 }
      );
    }

    if (!company || !position || !startDate) {
      return NextResponse.json(
        { error: 'Missing required employment information' },
        { status: 400 }
      );
    }

    // Create verification record in Supabase
    const { data: verification, error: dbError } = await supabase
      .from('verifications')
      .insert({
        candidate_name: candidateName,
        candidate_email: candidateEmail,
        candidate_phone: candidatePhone,
        linkedin_url: candidateLinkedIn,
        company,
        position,
        employment_start: startDate,
        employment_end: endDate || null,
        verification_options: verificationOptions,
        status: 'pending',
      })
      .select()
      .single();

    if (dbError) {
      console.error('Database error:', dbError);
      return NextResponse.json(
        { error: 'Failed to create verification record' },
        { status: 500 }
      );
    }

    // Call Python backend to start verification process
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    try {
      const backendResponse = await fetch(`${backendUrl}/api/v1/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          verification_id: verification.id,
          candidate_name: candidateName,
          candidate_email: candidateEmail,
          candidate_phone: candidatePhone,
          company,
          position,
          start_date: startDate,
          end_date: endDate,
          verification_options: verificationOptions,
        }),
      });

      if (!backendResponse.ok) {
        throw new Error(`Backend returned ${backendResponse.status}`);
      }
    } catch (backendError) {
      console.error('Backend error:', backendError);
      // Update verification status to failed
      await supabase
        .from('verifications')
        .update({ status: 'failed' })
        .eq('id', verification.id);
      
      return NextResponse.json(
        { error: 'Failed to start verification process' },
        { status: 500 }
      );
    }

    return NextResponse.json({
      verification_id: verification.id,
      status: 'pending',
      message: 'Verification started successfully',
    });

  } catch (error) {
    console.error('API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
