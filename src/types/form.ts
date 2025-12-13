export interface LoanFormData {
  // Step 1: Personal
  firstName: string;
  lastName: string;
  personalId: string;
  gender: string;
  birthYear: string;
  phone: string;
  address: string;

  // Step 2: Education
  educationLevel: string;
  university: string;

  // Step 3: Employment
  employmentStatus: string;
  companyName?: string;
  monthlySalary: string; // string for input, convert to number for logic
  experienceYears: string;

  // Step 4: Loan
  loanPurpose: string;
  loanDuration: string; // months
  loanAmount: string;
  additionalInfo?: string;

  // Step 5: Documents
  bankStatementName?: string;
  salaryStatementName?: string;
  bankStatementFile?: File;
  salaryStatementFile?: File;
  bankStatementUrl?: string;
  salaryStatementUrl?: string;
  bankStatementSize?: number;
  salaryStatementSize?: number;
  bankStatementMimeType?: string;
  salaryStatementMimeType?: string;
}

export const INITIAL_DATA: LoanFormData = {
  firstName: "",
  lastName: "",
  personalId: "",
  gender: "",
  birthYear: "",
  phone: "",
  address: "",
  educationLevel: "",
  university: "",
  employmentStatus: "",
  companyName: "",
  monthlySalary: "",
  experienceYears: "",
  loanPurpose: "",
  loanDuration: "",
  loanAmount: "",
  additionalInfo: "",
  bankStatementName: "",
  salaryStatementName: ""
};
