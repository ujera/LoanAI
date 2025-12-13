import { Input } from "@/components/ui/Input";
import { LoanFormData } from "@/types/form";
import { Upload, Loader2 } from "lucide-react";
import { useState } from "react";

interface StepProps {
  data: LoanFormData;
  onChange: (field: keyof LoanFormData, value: string | File) => void;
  errors: Partial<Record<keyof LoanFormData, string>>;
}

export function DocumentsStep({ data, onChange, errors }: StepProps) {
  const [uploadingBank, setUploadingBank] = useState(false);
  const [uploadingSalary, setUploadingSalary] = useState(false);

  const handleFileChange = (
    field: 'bankStatementFile' | 'salaryStatementFile',
    nameField: 'bankStatementName' | 'salaryStatementName',
    urlField: 'bankStatementUrl' | 'salaryStatementUrl',
    documentType: string
  ) => (e: React.ChangeEvent<HTMLInputElement>) => {
    const processFile = async () => {
      if (e.target.files && e.target.files[0]) {
        const file = e.target.files[0];
        onChange(field, file);
        onChange(nameField, file.name);
        
        // Upload to backend
        const isBank = field === 'bankStatementFile';
        isBank ? setUploadingBank(true) : setUploadingSalary(true);
        
        try {
          const formData = new FormData();
          formData.append('file', file);
          formData.append('documentType', documentType);
          
          const response = await fetch('/api/upload-document', {
            method: 'POST',
            body: formData,
          });
          
          if (!response.ok) {
            const errorData = await response.json().catch(() => ({ 
              error: 'Upload failed', 
              details: `Server returned ${response.status}` 
            }));
            throw new Error(errorData.details || errorData.error || 'Upload failed');
          }
          
          const result = await response.json();
          onChange(urlField, result.fileUrl);
          
          // Store file metadata
          if (isBank) {
            onChange('bankStatementSize' as any, result.fileSize);
            onChange('bankStatementMimeType' as any, result.mimeType);
          } else {
            onChange('salaryStatementSize' as any, result.fileSize);
            onChange('salaryStatementMimeType' as any, result.mimeType);
          }
        } catch (error) {
          console.error('Upload error:', error);
          
          // Get detailed error message from response
          let errorMessage = 'Failed to upload file.';
          if (error instanceof Error) {
            errorMessage = error.message;
          }
          
          alert(
            `Upload Error: ${errorMessage}\n\n` +
            `Please ensure:\n` +
            `1. Cloud Storage is configured (check .env)\n` +
            `2. GCP credentials are in config/gcp-credentials.json\n` +
            `3. File is under 10MB\n\n` +
            `See TROUBLESHOOTING.md for help.`
          );
          
          // Clear the file selection on error
          onChange(nameField, '');
          onChange(field, '' as any);
        } finally {
          isBank ? setUploadingBank(false) : setUploadingSalary(false);
        }
      }
    };
    
    processFile();
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
      <div className="p-4 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
        <h3 className="font-medium text-slate-900 dark:text-slate-100 mb-2 flex items-center gap-2">
          {uploadingBank ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
          Bank Statement
        </h3>
        <p className="text-xs text-slate-500 mb-4">Latest 3 months of bank statements.</p>
        <div className="relative">
          <Input
            type="file"
            onChange={handleFileChange('bankStatementFile', 'bankStatementName', 'bankStatementUrl', 'bank_statement')}
            error={errors.bankStatementName}
            accept=".pdf,.png,.jpg,.jpeg"
            disabled={uploadingBank}
            className="file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-slate-100 file:text-slate-700 hover:file:bg-slate-200 dark:file:bg-slate-800 dark:file:text-slate-200"
          />
          {data.bankStatementName && (
            <p className="text-sm text-emerald-600 mt-1">
              {uploadingBank ? 'Uploading...' : `✓ Selected: ${data.bankStatementName}`}
            </p>
          )}
        </div>
      </div>

      <div className="p-4 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
        <h3 className="font-medium text-slate-900 dark:text-slate-100 mb-2 flex items-center gap-2">
          {uploadingSalary ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
          Salary Statement
        </h3>
        <p className="text-xs text-slate-500 mb-4">Latest payslip or employment proof.</p>
        <div className="relative">
          <Input
            type="file"
            onChange={handleFileChange('salaryStatementFile', 'salaryStatementName', 'salaryStatementUrl', 'salary_statement')}
            error={errors.salaryStatementName}
            accept=".pdf,.png,.jpg,.jpeg"
            disabled={uploadingSalary}
            className="file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-slate-100 file:text-slate-700 hover:file:bg-slate-200 dark:file:bg-slate-800 dark:file:text-slate-200"
          />
          {data.salaryStatementName && (
            <p className="text-sm text-emerald-600 mt-1">
              {uploadingSalary ? 'Uploading...' : `✓ Selected: ${data.salaryStatementName}`}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
