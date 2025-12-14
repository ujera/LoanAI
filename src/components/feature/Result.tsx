import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { CheckCircle, XCircle, Clock, AlertCircle } from "lucide-react";

interface AIDecision {
  decision: string;
  confidence_score: number;
  risk_score: number;
  reasoning: string;
  loan_amount?: number;
  interest_rate?: number;
  loan_duration?: number;
  conditions?: string[];
}

interface ResultProps {
  customerId: string;
  aiDecision: AIDecision | null;
  isLoading: boolean;
  onReset: () => void;
}

export function Result({ customerId, aiDecision, isLoading, onReset }: ResultProps) {
  if (isLoading || !aiDecision) {
    return (
      <div className="flex flex-col items-center justify-center space-y-6 py-12">
        <div className="relative flex items-center justify-center w-16 h-16">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
        </div>
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold dark:text-white">
            Processing Your Application
          </h2>
          <p className="text-slate-500 dark:text-slate-400 max-w-sm">
            Our AI agents are analyzing your application. This may take a few moments...
          </p>
        </div>
      </div>
    );
  }

  const isApproved = aiDecision.decision === "APPROVED";
  const isRejected = aiDecision.decision === "REJECTED";
  const isReview = aiDecision.decision === "MANUAL_REVIEW";
  
  // Calculate display score (inverse of risk for visual appeal)
  // Ensure we have valid numbers to prevent NaN
  const riskScore = typeof aiDecision.risk_score === 'number' && !isNaN(aiDecision.risk_score) 
    ? aiDecision.risk_score 
    : 50;
  const displayScore = Math.max(10, Math.min(100, 100 - riskScore));
  
  return (
    <div className="flex flex-col items-center justify-center space-y-6 animate-in zoom-in duration-500">
      {/* Icon and Status */}
      <div className="flex flex-col items-center space-y-4">
        {isApproved && (
          <>
            <div className="flex items-center justify-center w-24 h-24 rounded-full bg-emerald-100 dark:bg-emerald-900/30">
              <CheckCircle className="text-emerald-600 dark:text-emerald-400 w-16 h-16" />
            </div>
            <div className="text-center space-y-2">
              <h2 className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">
                Congratulations!
              </h2>
              <p className="text-lg text-slate-700 dark:text-slate-300">
                Your loan application has been approved
              </p>
            </div>
          </>
        )}
        
        {isReview && (
          <>
            <div className="flex items-center justify-center w-24 h-24 rounded-full bg-amber-100 dark:bg-amber-900/30">
              <Clock className="text-amber-600 dark:text-amber-400 w-16 h-16" />
            </div>
            <div className="text-center space-y-2">
              <h2 className="text-3xl font-bold text-amber-600 dark:text-amber-400">
                Under Review
              </h2>
              <p className="text-lg text-slate-700 dark:text-slate-300">
                We will contact you soon!
              </p>
            </div>
          </>
        )}
        
        {isRejected && (
          <>
            <div className="flex items-center justify-center w-24 h-24 rounded-full bg-red-100 dark:bg-red-900/30">
              <XCircle className="text-red-600 dark:text-red-400 w-16 h-16" />
            </div>
            <div className="text-center space-y-2">
              <h2 className="text-3xl font-bold text-red-600 dark:text-red-400">
                Not Approved
              </h2>
              <p className="text-lg text-slate-700 dark:text-slate-300">
                Sorry, but you didn&apos;t pass the criteria
              </p>
            </div>
          </>
        )}
      </div>

      {/* Score Visualization */}
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
            className={
              isApproved
                ? "text-emerald-500"
                : isReview
                ? "text-amber-500"
                : "text-red-500"
            }
            strokeWidth="8"
            strokeDasharray={365}
            strokeDashoffset={365 - (365 * displayScore) / 100}
            strokeLinecap="round"
            stroke="currentColor"
            fill="transparent"
            r="58"
            cx="64"
            cy="64"
            style={{ transition: "stroke-dashoffset 1s ease-in-out" }}
          />
        </svg>
        <div className="absolute text-center">
          <span className="block text-2xl font-bold dark:text-white">
            {displayScore}
          </span>
          <span className="block text-xs text-slate-500 dark:text-slate-400">
            Score
          </span>
        </div>
      </div>

      {/* Loan Details (if approved) */}
      {isApproved && aiDecision.loan_amount && (
        <div className="w-full p-4 rounded-lg bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800">
          <h3 className="font-semibold text-emerald-900 dark:text-emerald-100 mb-3">
            Approved Loan Terms
          </h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-slate-600 dark:text-slate-400">Amount:</span>
              <p className="font-bold text-emerald-700 dark:text-emerald-300">
                ${aiDecision.loan_amount?.toLocaleString()}
              </p>
            </div>
            {aiDecision.interest_rate && (
              <div>
                <span className="text-slate-600 dark:text-slate-400">Interest Rate:</span>
                <p className="font-bold text-emerald-700 dark:text-emerald-300">
                  {aiDecision.interest_rate}%
                </p>
              </div>
            )}
            {aiDecision.loan_duration && (
              <div>
                <span className="text-slate-600 dark:text-slate-400">Duration:</span>
                <p className="font-bold text-emerald-700 dark:text-emerald-300">
                  {aiDecision.loan_duration} months
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Conditions (if any) */}
      {aiDecision.conditions && aiDecision.conditions.length > 0 && (
        <div className="w-full p-4 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="text-slate-600 dark:text-slate-400 w-5 h-5" />
            <span className="font-semibold text-sm text-slate-900 dark:text-slate-100">
              Additional Requirements
            </span>
          </div>
          <ul className="text-xs text-slate-600 dark:text-slate-400 space-y-1 ml-7">
            {aiDecision.conditions.map((condition, index) => (
              <li key={index} className="list-disc">
                {condition}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* AI Assessment Info */}
      <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-900 w-full border border-slate-200 dark:border-slate-800">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
          <span className="font-semibold text-sm text-slate-900 dark:text-slate-100">
            AI Multi-Agent Analysis
          </span>
        </div>
        <p className="text-xs text-slate-600 dark:text-slate-400">
          Your application was analyzed by our Bank Statement, Salary Verification, and External Verification agents.
          <span className="block mt-1 font-medium">
            Confidence: {Math.round((aiDecision.confidence_score || 0) * 100)}% | Risk Level: {riskScore}/100
          </span>
        </p>
      </div>

      {/* Application ID */}
      <div className="text-center text-xs text-slate-500 dark:text-slate-400">
        Application ID: {customerId.slice(0, 8)}...
      </div>

      <Button onClick={onReset} variant="outline" className="w-full">
        Submit New Application
      </Button>
    </div>
  );
}
