"use client";

import { useState } from "react";
import { LoanForm } from "@/components/feature/LoanForm";
import { LandingPage } from "@/components/feature/LandingPage";
import { cn } from "@/lib/utils";
import { useRouter } from "next/navigation";

export default function Home() {
  const [hasStarted, setHasStarted] = useState(false);
  const router = useRouter();

  const handleAdminStart = () => {
    router.push('/admin');
  };

  return (
    <div className="min-h-screen font-[family-name:var(--font-geist-sans)]">
      
      {/* Landing Page Layer */}
      <div 
        className={cn(
          "transition-all duration-700 ease-in-out absolute inset-0 z-10 bg-[#030712]",
          hasStarted ? "-translate-y-full opacity-0 pointer-events-none" : "translate-y-0 opacity-100"
        )}
      >
        <LandingPage onStart={() => setHasStarted(true)} onAdminStart={handleAdminStart} />
      </div>

      {/* App Layer */}
      <div 
        className={cn(
          "min-h-screen transition-all duration-700 ease-in-out flex flex-col items-center pt-10 sm:pt-20 px-4",
          hasStarted ? "opacity-100 translate-y-0 scale-100" : "opacity-0 translate-y-20 scale-95 pointer-events-none absolute inset-0"
        )}
      >
        {hasStarted && (
           <>
              <div className="text-center mb-10 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-300">
                <h2 className="text-3xl font-bold text-white mb-2">Loan Eligibility Simulator</h2>
                <p className="text-slate-400">Complete the steps below to verify your eligibility</p>
              </div>
              <LoanForm />
              
              <button 
                onClick={() => setHasStarted(false)}
                className="mt-8 text-slate-500 hover:text-white text-sm transition-colors"
              >
                ← Back to Home
              </button>
           </>
        )}
      </div>
    </div>
  );
}
