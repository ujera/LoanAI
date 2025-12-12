import { cn } from "@/lib/utils";
import { Check } from "lucide-react";

interface StepperProps {
  currentStep: number;
  totalSteps: number;
}

export function Stepper({ currentStep, totalSteps }: StepperProps) {
  const steps = Array.from({ length: totalSteps }, (_, i) => i + 1);

  return (
    <div className="flex items-center justify-center w-full mb-10">
      {steps.map((step, index) => {
        const isCompleted = step < currentStep;
        const isCurrent = step === currentStep;
        const isLast = index === steps.length - 1;

        return (
          <div key={step} className="flex items-center">
            <div
              className={cn(
                "relative flex items-center justify-center w-10 h-10 rounded-full text-sm font-bold transition-all duration-300",
                isCompleted
                  ? "bg-cyan-500 text-black shadow-[0_0_15px_rgba(6,182,212,0.5)]"
                  : isCurrent
                  ? "bg-indigo-600 text-white shadow-[0_0_15px_rgba(79,70,229,0.5)] border-2 border-indigo-400"
                  : "bg-white/5 text-slate-500 border border-white/10"
              )}
            >
              {isCompleted ? <Check className="w-5 h-5" /> : step}
              
              {isCurrent && (
                 <span className="absolute -bottom-6 text-[10px] font-medium text-indigo-300 uppercase tracking-wider whitespace-nowrap">
                   Step {step}
                 </span>
              )}
            </div>
            {!isLast && (
              <div
                className={cn(
                  "w-8 sm:w-16 h-0.5 mx-2 transition-all duration-500",
                  step < currentStep
                    ? "bg-gradient-to-r from-cyan-500 to-indigo-600"
                    : "bg-white/10"
                )}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
