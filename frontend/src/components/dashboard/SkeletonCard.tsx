import { Card, CardContent, CardHeader } from '@/src/components/ui/card';
import { Skeleton } from '@/src/components/ui/skeleton';

export function SkeletonStatCard() {
  return (
    <Card className="glass">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-2 flex-1">
            <Skeleton className="h-4 w-24 bg-gray-700" />
            <Skeleton className="h-8 w-16 bg-gray-700" />
          </div>
          <Skeleton className="h-12 w-12 rounded-lg bg-gray-700" />
        </div>
        <Skeleton className="h-3 w-20 mt-4 bg-gray-700" />
      </CardContent>
    </Card>
  );
}

export function SkeletonTableRow() {
  return (
    <div className="flex items-center gap-4 p-4 rounded-lg bg-gray-800/30 animate-pulse">
      <Skeleton className="h-10 w-10 rounded-full bg-gray-700" />
      <div className="flex-1 space-y-2">
        <Skeleton className="h-4 w-32 bg-gray-700" />
        <Skeleton className="h-3 w-48 bg-gray-700" />
      </div>
      <Skeleton className="h-6 w-20 rounded-full bg-gray-700" />
      <Skeleton className="h-8 w-24 rounded bg-gray-700" />
    </div>
  );
}

export function SkeletonReportSection() {
  return (
    <Card className="glass border-white/10">
      <CardHeader>
        <Skeleton className="h-6 w-48 bg-gray-700" />
      </CardHeader>
      <CardContent className="space-y-3">
        <Skeleton className="h-4 w-full bg-gray-700" />
        <Skeleton className="h-4 w-5/6 bg-gray-700" />
        <Skeleton className="h-4 w-4/6 bg-gray-700" />
      </CardContent>
    </Card>
  );
}
