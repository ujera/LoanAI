import { Input } from "@/components/ui/Input";
import { LoanFormData } from "@/types/form";
import { Upload } from "lucide-react";

interface StepProps {
  data: LoanFormData;
  onChange: (field: keyof LoanFormData, value: string) => void;
  errors: Partial<Record<keyof LoanFormData, string>>;
}

export function DocumentsStep({ data, onChange, errors }: StepProps) {
  const handleFileChange = (field: keyof LoanFormData) => (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onChange(field, e.target.files[0].name);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
      <div className="p-4 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
        <h3 className="font-medium text-slate-900 dark:text-slate-100 mb-2 flex items-center gap-2">
          <Upload className="w-4 h-4" /> Bank Statement
        </h3>
        <p className="text-xs text-slate-500 mb-4">Latest 3 months of bank statements.</p>
        <div className="relative">
          <Input
            type="file"
            onChange={handleFileChange("bankStatementName")}
            error={errors.bankStatementName}
            accept=".pdf,.png,.jpg,.jpeg"
            className="file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-slate-100 file:text-slate-700 hover:file:bg-slate-200 dark:file:bg-slate-800 dark:file:text-slate-200"
          />
          {data.bankStatementName && (
            <p className="text-sm text-emerald-600 mt-1">Selected: {data.bankStatementName}</p>
          )}
        </div>
      </div>

      <div className="p-4 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
        <h3 className="font-medium text-slate-900 dark:text-slate-100 mb-2 flex items-center gap-2">
          <Upload className="w-4 h-4" /> Salary Statement
        </h3>
        <p className="text-xs text-slate-500 mb-4">Latest payslip or employment proof.</p>
        <div className="relative">
          <Input
            type="file"
            onChange={handleFileChange("salaryStatementName")}
            error={errors.salaryStatementName}
            accept=".pdf,.png,.jpg,.jpeg"
            className="file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-slate-100 file:text-slate-700 hover:file:bg-slate-200 dark:file:bg-slate-800 dark:file:text-slate-200"
          />
          {data.salaryStatementName && (
            <p className="text-sm text-emerald-600 mt-1">Selected: {data.salaryStatementName}</p>
          )}
        </div>
      </div>
    </div>
  );
}
