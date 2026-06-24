interface PageHeaderProps {
  title: string;
  description?: string;
}

export function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <div className="mb-6 border-l-4 border-primary pl-3 md:pl-4">
      <h1 className="text-xl md:text-2xl font-bold tracking-tight leading-snug">{title}</h1>
      {description && <p className="text-base text-muted-foreground mt-1">{description}</p>}
    </div>
  );
}
