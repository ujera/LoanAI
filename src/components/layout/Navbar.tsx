"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Sparkles, Github } from "lucide-react";
import { cn } from "@/lib/utils";

export function Navbar() {
  const pathname = usePathname();
  const isHome = pathname === "/";

  return (
    <nav className={cn(
        "w-full py-6 px-4 md:px-8 flex justify-between items-center max-w-7xl mx-auto z-50",
        isHome ? "absolute top-0 left-0 right-0" : "relative bg-transparent"
    )}>
      <Link href="/" className="flex items-center gap-2 group">
        <div className="w-8 h-8 rounded-lg bg-indigo-500/20 border border-indigo-500/50 flex items-center justify-center transition-transform group-hover:scale-105">
           <Sparkles className="w-4 h-4 text-indigo-400" />
        </div>
        <span className="text-xl font-bold font-serif tracking-tight text-white">
          Loan<span className="text-indigo-400">AI</span> <span className="text-xs font-sans font-normal text-slate-500 uppercase tracking-widest ml-2 border border-white/10 px-2 py-0.5 rounded-full">Prototype</span>
        </span>
      </Link>
      
      <div className="hidden md:flex items-center gap-8">
          <Link href="/about" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">
            Process
          </Link>
           <Link href="/contact" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">
            Team
          </Link>
          <Link href="https://github.com/ujera/LoanAI" target="_blank" rel="noopener noreferrer">
            <Button
              variant="outline"
              className="text-sm gap-2 h-9"
            >
              <Github className="w-4 h-4" />
              Repo
            </Button>
          </Link>
          
      </div>

      {/* Mobile Menu Placeholder */}
      <div className="md:hidden">
          <Button variant="ghost" size="sm">Menu</Button>
      </div>
    </nav>
  );
}
