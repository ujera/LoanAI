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
    </div>
  );
}
