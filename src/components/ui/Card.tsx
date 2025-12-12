import { cn } from "@/lib/utils";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {}

export function Card({ className, ...props }: CardProps) {
  return (
    <div
      className={cn(
        "glass-panel rounded-2xl p-6 sm:p-8 text-slate-100",
        className
      )}
      {...props}
    />
  );
}
