import { FileText } from 'lucide-react';

interface Transcript {
  filename: string;
  content: string;
  timestamp: number;
}

interface TranscriptViewerProps {
  transcripts: Transcript[];
}

export function TranscriptViewer({ transcripts }: TranscriptViewerProps) {
  if (!transcripts || transcripts.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
        <p>No call transcripts available yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {transcripts.map((transcript, index) => (
        <div key={index} className="border rounded-lg p-6 bg-white">
          <div className="flex items-center gap-2 mb-4 pb-3 border-b">
            <FileText className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold text-gray-900">{transcript.filename}</h3>
            <span className="text-sm text-gray-500 ml-auto">
              {new Date(transcript.timestamp * 1000).toLocaleString()}
            </span>
          </div>
          <pre className="whitespace-pre-wrap text-sm text-gray-700 font-mono leading-relaxed">
            {transcript.content}
          </pre>
        </div>
      ))}
    </div>
  );
}
