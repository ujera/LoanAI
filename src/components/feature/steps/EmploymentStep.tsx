import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { LoanFormData } from "@/types/form";

interface StepProps {
  data: LoanFormData;
  onChange: (field: keyof LoanFormData, value: string) => void;
  errors: Partial<Record<keyof LoanFormData, string>>;
}

export function EmploymentStep({ data, onChange, errors }: StepProps) {
  const isUnemployed = data.employmentStatus === "unemployed";

  return (
    <div className="space-y-4 animate-in fade-in slide-in-from-right-4 duration-300">
      <Select
        label="Employment Status"
        options={[
          { label: "Employed", value: "employed" },
          { label: "Self-employed", value: "self_employed" },
          { label: "Unemployed", value: "unemployed" },
        ]}
        value={data.employmentStatus}
        onChange={(e) => onChange("employmentStatus", e.target.value)}
        error={errors.employmentStatus}
        placeholder="Select status"
      />
      
      {!isUnemployed && (
        <>
          <Input
            label="Company Name"
            value={data.companyName}
            onChange={(e) => onChange("companyName", e.target.value)}
            error={errors.companyName}
            placeholder="Company Ltd."
          />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
             <Input
              label="Monthly Salary ($)"
              type="number"
              value={data.monthlySalary}
              onChange={(e) => onChange("monthlySalary", e.target.value)}
              error={errors.monthlySalary}
              placeholder="5000"
            />
             <Input
              label="Experience (Years)"
              type="number"
              value={data.experienceYears}
              onChange={(e) => onChange("experienceYears", e.target.value)}
              error={errors.experienceYears}
              placeholder="3"
            />
          </div>
        </>
      )}
    </div>
  );
}
