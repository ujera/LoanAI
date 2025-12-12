import { Navbar } from "@/components/layout/Navbar";
import { Cpu, Database, Layout } from "lucide-react";

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-[#030712] text-slate-200 font-sans">
      <Navbar />
      
      <main className="max-w-4xl mx-auto px-4 py-20">
        <div className="text-center mb-16 space-y-4">
          <h1 className="text-4xl md:text-5xl font-serif text-white">How It Works</h1>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto font-mono text-sm leading-relaxed">
            DEEP DIVE INTO THE ARCHITECTURE
          </p>
        </div>

        <div className="space-y-12">
          <div className="glass-panel p-8 rounded-2xl border-l-4 border-indigo-500">
            <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
              <Cpu className="w-6 h-6 text-indigo-400" />
              The Algorithm
            </h2>
            <p className="text-slate-300 leading-relaxed mb-4">
              LoanAI uses a weighted scoring model to evaluate applicant eligibility in real-time. Unlike traditional banking systems that rely on slow manual review, our system aggregates data points—including income stability, debt-to-income ratio, and career trajectory—to generate an instant `eligibility_score`.
            </p>
            <div className="bg-black/40 p-4 rounded-lg font-mono text-xs text-indigo-300 overflow-x-auto">
              <code>
                const score = (salary * 0.4) + (employment_history * 0.3) + (credit_factors * 0.3);
              </code>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="glass-panel p-6 rounded-xl">
               <h3 className="text-xl font-bold text-white mb-3 flex items-center gap-2">
                 <Layout className="w-5 h-5 text-cyan-400" />
                 Frontend Architecture
               </h3>
               <ul className="space-y-2 text-slate-400 text-sm list-disc list-inside">
                 <li>Next.js 15 (App Router)</li>
                 <li>React Server Components</li>
                 <li>Tailwind CSS v4 (Alpha)</li>
                 <li>Framer Motion (Animations)</li>
               </ul>
            </div>

            <div className="glass-panel p-6 rounded-xl">
               <h3 className="text-xl font-bold text-white mb-3 flex items-center gap-2">
                 <Database className="w-5 h-5 text-emerald-400" />
                 Data Privacy
               </h3>
               <p className="text-slate-400 text-sm leading-relaxed">
                 Since this is a client-side prototype, no personal data is actually sent to a server. All processing happens locally in your browser's memory, ensuring complete privacy during this demonstration.
               </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
