"use client";

import { Button } from "@/components/ui/Button";
import { ArrowRight, Code2, Zap, Cpu } from "lucide-react";
import { Navbar } from "@/components/layout/Navbar";
import Link from "next/link";

interface LandingPageProps {
  onStart: () => void;
}

export function LandingPage({ onStart }: LandingPageProps) {
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
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-xs font-mono text-indigo-300 mb-6 animate-in fade-in slide-in-from-bottom-4 duration-1000">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
            </span>
            Hackathon Submission #2025
          </div>
          
          <h1 className="text-5xl md:text-7xl lg:text-8xl font-serif font-medium tracking-tight text-white animate-in zoom-in-50 duration-1000 leading-[1.1]">
            AI-Driven Loan <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-cyan-400 italic">Prediction Model</span>
          </h1>
          
          <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-100 font-light">
            An experimental prototype exploring how Machine Learning can optimize financial eligibility assessments in real-time. Built in 24 hours.
          </p>
          <div>
            <Button onClick={onStart} variant="primary" className="h-14 px-10 text-lg rounded-full font-mono">
              run_simulation() <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
              <Link href="https://github.com/ujera/LoanAI">
                <Button variant="outline" className="h-14 px-10 text-lg rounded-full border-white/10 hover:bg-white/5 font-mono text-slate-400">
                  View Source Code
                </Button>
              </Link>
          </div>
        </div>

        {/* Tech Stack / Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto w-full mt-12 mb-20 animate-in fade-in duration-1000 delay-500 px-4">
           <FeatureCard 
             icon={<Cpu className="w-5 h-5 text-indigo-400" />}
             title="Next.js 15 Engine"
             description="Powered by the latest App Router and React Server Components for seamless transitions."
           />
           <FeatureCard 
             icon={<Zap className="w-5 h-5 text-amber-300" />}
             title="Instant Feedback"
             description="Local predictive algorithm provides immediate eligibility scoring without server latency."
           />
           <FeatureCard 
             icon={<Code2 className="w-5 h-5 text-cyan-300" />}
             title="Modern Stack"
             description="Built with Tailwind CSS v4, TypeScript, and Framer Motion-like CSS animations."
           />
        </div>
      </main>
      
      <footer className="w-full py-6 text-center border-t border-white/5 bg-black/20 backdrop-blur-md">
        <p className="text-slate-600 text-xs font-mono">
          Built for the Hackathon 2025 • Open Source • MIT License
        </p>
      </footer>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="bg-white/5 border border-white/5 p-6 rounded-lg text-left hover:bg-white/10 transition-all duration-300">
      <div className="flex items-center gap-3 mb-3">
        {icon}
        <h3 className="font-mono font-bold text-white text-sm uppercase tracking-wide">{title}</h3>
      </div>
      <p className="text-slate-400 text-sm leading-relaxed">{description}</p>
    </div>
  );
}
