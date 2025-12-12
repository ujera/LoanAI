import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { LoanFormData } from "@/types/form";

interface StepProps {
  data: LoanFormData;
  onChange: (field: keyof LoanFormData, value: string) => void;
  errors: Partial<Record<keyof LoanFormData, string>>;
}

export function EducationStep({ data, onChange, errors }: StepProps) {
  return (
    <div className="space-y-4 animate-in fade-in slide-in-from-right-4 duration-300">
      <Select
        label="Education Level"
        options={[
          { label: "High School", value: "high_school" },
          { label: "Bachelor", value: "bachelor" },
          { label: "Master", value: "master" },
          { label: "PhD", value: "phd" },
        ]}
        value={data.educationLevel}
        onChange={(e) => onChange("educationLevel", e.target.value)}
        error={errors.educationLevel}
        placeholder="Select level"
      />
      
      <Input
        label="University Name"
        value={data.university}
        onChange={(e) => onChange("university", e.target.value)}
        error={errors.university}
        placeholder="University of ..."
      />
    </div>
  );
}
