"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useApi } from "@/hooks/use-api";

interface ChartCardProps<T> {
  title: string;
  path: string;
  children: (data: T) => React.ReactNode;
}

export function ChartCard<T>({ title, path, children }: ChartCardProps<T>) {
  const { data, loading, error } = useApi<T>(path);

  return (
    <Card className="animate-in fade-in slide-in-from-bottom-2 duration-500 transition-shadow hover:shadow-md">
      <CardHeader>
        <CardTitle className="text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {loading && <Skeleton className="h-[300px] w-full" />}
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        {data && children(data)}
      </CardContent>
    </Card>
  );
}
