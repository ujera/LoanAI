import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { CheckCircle, XCircle } from "lucide-react";

interface ResultProps {
  score: number;
  onReset: () => void;
}

export function Result({ score, onReset }: ResultProps) {
  const isEligible = score >= 70;
  
  return (
    <div className="flex flex-col items-center justify-center space-y-6 animate-in zoom-in duration-500">
      <div className="relative flex items-center justify-center w-32 h-32">
        <svg className="w-full h-full transform -rotate-90">
          <circle
            className="text-slate-200 dark:text-slate-800"
            strokeWidth="8"
            stroke="currentColor"
            fill="transparent"
            r="58"
            cx="64"
            cy="64"
          />
          <circle
            className={isEligible ? "text-emerald-500" : "text-amber-500"}
            strokeWidth="8"
            strokeDasharray={365}
            strokeDashoffset={365 - (365 * score) / 100}
            strokeLinecap="round"
            stroke="currentColor"
            fill="transparent"
            r="58"
            cx="64"
            cy="64"
            style={{ transition: "stroke-dashoffset 1s ease-in-out" }}
          />
        </svg>
        <span className="absolute text-2xl font-bold dark:text-white">
          {score}
        </span>
      </div>

      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold dark:text-white">
          {isEligible ? "Likely Eligible" : "Review Needed"}
        </h2>
        <p className="text-slate-500 dark:text-slate-400 max-w-sm">
          {isEligible
            ? "Based on the provided details, you have a strong profile for this loan."
            : "Your profile indicates some risk factors. Consider modifying the loan amount or duration."}
        </p>
      </div>

      <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-900 w-full">
        <div className="flex items-center gap-2 mb-2">
           {isEligible ? <CheckCircle className="text-emerald-500 w-5 h-5"/> : <XCircle className="text-amber-500 w-5 h-5"/>}
           <span className="font-semibold text-sm">Automated Assessment</span>
        </div>
        <p className="text-xs text-slate-500">
          This is a demonstration tool. No real credit check was performed.
        </p>
      </div>

      <Button onClick={onReset} variant="outline" className="w-full">
        Start Over
      </Button>
    </div>
  );
}
