import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { LoanFormData } from "@/types/form";

interface StepProps {
  data: LoanFormData;
  onChange: (field: keyof LoanFormData, value: string) => void;
  errors: Partial<Record<keyof LoanFormData, string>>;
}

export function PersonalStep({ data, onChange, errors }: StepProps) {
  return (
    <div className="space-y-4 animate-in fade-in slide-in-from-right-4 duration-300">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input
          label="First Name"
          value={data.firstName}
          onChange={(e) => onChange("firstName", e.target.value)}
          error={errors.firstName}
          placeholder="John"
        />
        <Input
          label="Last Name"
          value={data.lastName}
          onChange={(e) => onChange("lastName", e.target.value)}
          error={errors.lastName}
          placeholder="Doe"
        />
      </div>
      
      <Input
        label="Personal ID Number"
        value={data.personalId}
        onChange={(e) => onChange("personalId", e.target.value)}
        error={errors.personalId}
        placeholder="1234567890"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Select
          label="Gender"
          options={[
            { label: "Male", value: "male" },
            { label: "Female", value: "female" },
            { label: "Other", value: "other" },
          ]}
          value={data.gender}
          onChange={(e) => onChange("gender", e.target.value)}
          error={errors.gender}
          placeholder="Select gender"
        />
        <Input
          label="Year of Birth"
          type="number"
          value={data.birthYear}
          onChange={(e) => {
            const value = e.target.value;
            // Only allow 4-digit years
            if (value.length <= 4) {
              onChange("birthYear", value);
            }
          }}
          error={errors.birthYear}
          placeholder="1990"
          maxLength={4}
        />
      </div>

      <Input
        label="Phone Number"
        type="tel"
        value={data.phone}
        onChange={(e) => onChange("phone", e.target.value)}
        error={errors.phone}
        placeholder="+1 234 567 890"
      />

      <Input
        label="Address"
        value={data.address}
        onChange={(e) => onChange("address", e.target.value)}
        error={errors.address}
        placeholder="123 Main St, City, Country"
      />
    </div>
  );
}
