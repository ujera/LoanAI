"use client";

import { Button } from "@/components/ui/Button";
import { ArrowRight, User, Shield } from "lucide-react";
import { Navbar } from "@/components/layout/Navbar";
import { useRouter } from "next/navigation";

interface LandingPageProps {
  onStart: () => void;
  onAdminStart?: () => void;
}

export function LandingPage({ onStart, onAdminStart }: LandingPageProps) {
  const router = useRouter();

  const handleAdminClick = () => {
    if (onAdminStart) {
      onAdminStart();
    } else {
      router.push('/admin');
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />

      {/* Hero Section */}
      <main className="flex-1 flex flex-col items-center justify-center text-center px-4 md:px-6 relative overflow-hidden mt-[-60px]">
        
        {/* Background Grid - classic dev/hackathon vibe */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none" />
        
        {/* Glows */}
        <div className="absolute top-0 transform -translate-x-1/2 left-1/2 w-[600px] h-[300px] bg-indigo-500/20 rounded-[100%] blur-[100px] pointer-events-none" />

        <div className="relative z-10 max-w-5xl mx-auto space-y-8 py-20">
          <h1 className="text-5xl md:text-7xl lg:text-8xl font-serif font-medium tracking-tight text-white animate-in zoom-in-50 duration-1000 leading-[1.1]">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-cyan-400">LoanAI</span>
          </h1>
          
          <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-100 font-light">
            An experimental prototype exploring how Machine Learning can optimize financial eligibility assessments in real-time. Built in 24 hours.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mt-8">
            <Button 
              onClick={onStart} 
              variant="primary" 
              className="h-14 px-10 text-lg rounded-full font-mono min-w-[200px]"
            >
              <User className="mr-2 w-5 h-5" />
              User Login
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
            <Button 
              onClick={handleAdminClick} 
              variant="outline" 
              className="h-14 px-10 text-lg rounded-full border-indigo-500/50 hover:bg-indigo-500/10 font-mono text-indigo-300 min-w-[200px]"
            >
              <Shield className="mr-2 w-5 h-5" />
              Admin Login
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </div>
        </div>
      </main>
      
      
    </div>
  );
}
