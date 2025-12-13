import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { LoanFormData } from "@/types/form";

interface StepProps {
  data: LoanFormData;
  onChange: (field: keyof LoanFormData, value: string) => void;
  errors: Partial<Record<keyof LoanFormData, string>>;
}

export function LoanDetailsStep({ data, onChange, errors }: StepProps) {
  return (
    <div className="space-y-4 animate-in fade-in slide-in-from-right-4 duration-300">
      <Select
        label="Loan Purpose"
        options={[
          { label: "Mortgage", value: "mortgage" },
          { label: "Vehicle", value: "vehicle" },
          { label: "Personal", value: "personal" },
          { label: "Education", value: "education" },
          { label: "Business", value: "business" },
        ]}
        value={data.loanPurpose}
        onChange={(e) => onChange("loanPurpose", e.target.value)}
        error={errors.loanPurpose}
        placeholder="Select purpose"
      />
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input
          label="Loan Duration (Months)"
          type="number"
          value={data.loanDuration}
          onChange={(e) => onChange("loanDuration", e.target.value)}
          error={errors.loanDuration}
          placeholder="24"
        />
        <Input
          label="Total Loan Amount ($)"
          type="number"
          value={data.loanAmount}
          onChange={(e) => onChange("loanAmount", e.target.value)}
          error={errors.loanAmount}
          placeholder="10000"
        />
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium leading-none text-slate-400">
          Tell us more about your situation
        </label>
        <textarea
          value={data.additionalInfo || ""}
          onChange={(e) => onChange("additionalInfo", e.target.value)}
          placeholder="Please describe your financial situation, loan purpose, and any additional details that might help us assess your application..."
          rows={5}
          className="flex w-full rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all resize-none"
        />
        <p className="text-xs text-slate-500">Optional: Share any relevant information about your situation</p>
      </div>
    </div>
  );
}
