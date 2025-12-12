"use client";

import { Navbar } from "@/components/layout/Navbar";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Github, Twitter, Linkedin } from "lucide-react";

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-[#030712] text-slate-200 font-sans">
      <Navbar />
      
      <main className="max-w-4xl mx-auto px-4 py-20">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-serif text-white mb-4">The Team</h1>
          <p className="text-xl text-slate-400 font-mono text-sm">
            BUILT DURING THE 2025 HACKATHON
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-2xl mx-auto">
          {/* Developer Card */}
          <Card className="glass-panel text-center hover:bg-white/5 transition-all duration-300">
             <div className="w-24 h-24 mx-auto rounded-full bg-indigo-500/20 flex items-center justify-center mb-6 border-2 border-indigo-500/30 text-2xl font-bold text-indigo-300">
               DV
             </div>
             <h3 className="text-xl font-bold text-white mb-1">Lead Developer</h3>
             <p className="text-slate-400 text-sm mb-6">Full Stack Engineer & UI Designer</p>
             
             <div className="flex justify-center gap-4">
               <Button variant="ghost" size="sm" className="w-10 h-10 p-0 rounded-full bg-white/5 hover:bg-white/10">
                 <Github className="w-4 h-4" />
               </Button>
               <Button variant="ghost" size="sm" className="w-10 h-10 p-0 rounded-full bg-white/5 hover:bg-white/10">
                 <Twitter className="w-4 h-4" />
               </Button>
               <Button variant="ghost" size="sm" className="w-10 h-10 p-0 rounded-full bg-white/5 hover:bg-white/10">
                 <Linkedin className="w-4 h-4" />
               </Button>
             </div>
          </Card>

          {/* Project Links */}
          <div className="space-y-4">
             <div className="p-6 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 transition-colors cursor-pointer">
               <h3 className="text-white font-bold mb-2 flex items-center gap-2">
                 <Github className="w-4 h-4" /> Source Code
               </h3>
               <p className="text-slate-400 text-sm">Check out the documentation and contribute to the repo.</p>
             </div>
             
             <div className="p-6 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 transition-colors cursor-pointer">
               <h3 className="text-white font-bold mb-2">DevPost Submission</h3>
               <p className="text-slate-400 text-sm">View our hackathon entry details, video demo, and judge comments.</p>
             </div>
          </div>
        </div>
      </main>
    </div>
  );
}
