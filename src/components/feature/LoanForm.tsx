"use client";

import React, { useState } from "react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Stepper } from "@/components/ui/Stepper";
import { LoanFormData, INITIAL_DATA } from "@/types/form";
import { PersonalStep } from "./steps/PersonalStep";
import { EducationStep } from "./steps/EducationStep";
import { EmploymentStep } from "./steps/EmploymentStep";
import { LoanDetailsStep } from "./steps/LoanDetailsStep";
import { DocumentsStep } from "./steps/DocumentsStep";
import { Result } from "./Result";
import { ChevronRight, ChevronLeft } from "lucide-react";

export function LoanForm() {
  const [step, setStep] = useState(1);
  const [data, setData] = useState<LoanFormData>(INITIAL_DATA);
  const [errors, setErrors] = useState<Partial<Record<keyof LoanFormData, string>>>({});
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [score, setScore] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const totalSteps = 5;

  const handleChange = (field: keyof LoanFormData, value: string | File) => {
    setData((prev) => ({ ...prev, [field]: value }));
    // Clear error when user types
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: "" }));
    }
  };

  const validateStep = (currentStep: number): boolean => {
    const newErrors: Partial<Record<keyof LoanFormData, string>> = {};
    let isValid = true;

    const requireField = (field: keyof LoanFormData, message = "Required") => {
      if (!data[field] || data[field].trim() === "") {
        newErrors[field] = message;
        isValid = false;
      }
    };

    if (currentStep === 1) {
      requireField("firstName");
      requireField("lastName");
      requireField("personalId");
      requireField("gender");
      requireField("birthYear");
      
      // Validate birth year format
      if (data.birthYear && (data.birthYear.length !== 4 || isNaN(Number(data.birthYear)))) {
        newErrors.birthYear = "Please enter a valid 4-digit year";
        isValid = false;
      }
      
      requireField("phone");
      requireField("address");
    } else if (currentStep === 2) {
      requireField("educationLevel");
      requireField("university");
    } else if (currentStep === 3) {
      requireField("employmentStatus");
      if (data.employmentStatus !== "unemployed") {
        requireField("companyName");
        requireField("monthlySalary");
        requireField("experienceYears");
      }
    } else if (currentStep === 4) {
      requireField("loanPurpose");
      requireField("loanDuration");
      requireField("loanAmount");
    } else if (currentStep === 5) {
      if (!data.bankStatementName) {
        newErrors.bankStatementName = "Please upload a bank statement";
        isValid = false;
      }
      if (!data.salaryStatementName) {
        newErrors.salaryStatementName = "Please upload a salary statement";
        isValid = false;
      }
    }

    setErrors(newErrors);
    return isValid;
  };

  const handleNext = () => {
    if (validateStep(step)) {
      setStep((prev) => Math.min(prev + 1, totalSteps));
    }
  };

  const handleBack = () => {
    setStep((prev) => Math.max(prev - 1, 1));
  };

  const calculateScore = () => {
    // Mock logic
    let tempScore = 50; // Base score

    // Salary
    const salary = parseInt(data.monthlySalary || "0");
    if (salary > 5000) tempScore += 20;
    else if (salary > 2000) tempScore += 10;

    // Employment
    if (data.employmentStatus === "employed") tempScore += 10;
    else if (data.employmentStatus === "self_employed") tempScore += 5;

    // Education
    if (["master", "phd"].includes(data.educationLevel)) tempScore += 5;

    // Loan Amount Ratio (simple check)
    const amount = parseInt(data.loanAmount || "0");
    if (amount < salary * 12) tempScore += 10;
    else tempScore -= 10;

    // Cap at 100
    if (tempScore > 100) tempScore = 98;
    if (tempScore < 0) tempScore = 15;
    
    return tempScore;
  };

  const handleSubmit = async () => {
    if (!validateStep(step)) return;

    setIsSubmitting(true);
    
    try {
      // Submit form data to backend
      const response = await fetch('/api/loan-application', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          firstName: data.firstName,
          lastName: data.lastName,
          personalId: data.personalId,
          gender: data.gender,
          birthYear: data.birthYear,
          phone: data.phone,
          address: data.address,
          educationLevel: data.educationLevel,
          university: data.university,
          employmentStatus: data.employmentStatus,
          companyName: data.companyName,
          monthlySalary: data.monthlySalary,
          experienceYears: data.experienceYears,
          loanPurpose: data.loanPurpose,
          loanDuration: data.loanDuration,
          loanAmount: data.loanAmount,
          additionalInfo: data.additionalInfo,
          bankStatementUrl: data.bankStatementUrl,
          salaryStatementUrl: data.salaryStatementUrl,
          bankStatementSize: data.bankStatementSize,
          salaryStatementSize: data.salaryStatementSize,
          bankStatementMimeType: data.bankStatementMimeType,
          salaryStatementMimeType: data.salaryStatementMimeType,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
        console.error('API Error:', errorData);
        throw new Error(errorData.error || errorData.details || 'Failed to submit application');
      }

      const result = await response.json();
      console.log('Application submitted:', result);

      // Calculate eligibility score
      const calculatedScore = calculateScore();
      setScore(calculatedScore);
      setIsSubmitted(true);
    } catch (error) {
      console.error('Error submitting application:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to submit application. Please try again.';
      alert(`Error: ${errorMessage}\n\nPlease ensure:\n1. Cloud SQL Proxy is running\n2. Backend services are available\n3. All required fields are filled`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setData(INITIAL_DATA);
    setStep(1);
    setIsSubmitted(false);
    setScore(0);
    setErrors({});
  };

  if (isSubmitted) {
    return (
      <Card className="w-full max-w-lg mx-auto mt-10">
        <Result score={score} onReset={handleReset} />
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-2xl mx-auto mt-6 md:mt-10">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
          Check Eligibility
        </h1>
        <p className="text-slate-500 dark:text-slate-400">
          Step {step} of {totalSteps}
        </p>
      </div>

      <Stepper currentStep={step} totalSteps={totalSteps} />

      <div className="min-h-[300px]">
        {step === 1 && (
          <PersonalStep data={data} onChange={handleChange} errors={errors} />
        )}
        {step === 2 && (
          <EducationStep data={data} onChange={handleChange} errors={errors} />
        )}
        {step === 3 && (
          <EmploymentStep data={data} onChange={handleChange} errors={errors} />
        )}
        {step === 4 && (
          <LoanDetailsStep data={data} onChange={handleChange} errors={errors} />
        )}
        {step === 5 && (
          <DocumentsStep data={data} onChange={handleChange} errors={errors} />
        )}
      </div>

      <div className="flex justify-between mt-8 pt-4 border-t border-slate-100 dark:border-slate-800">
        <Button
          variant="secondary"
          onClick={handleBack}
          disabled={step === 1 || isSubmitting}
          className={step === 1 ? "invisible" : ""}
        >
          <ChevronLeft className="w-4 h-4 mr-2" />
          Back
        </Button>

        {step < totalSteps ? (
          <Button onClick={handleNext}>
            Next
            <ChevronRight className="w-4 h-4 ml-2" />
          </Button>
        ) : (
          <Button onClick={handleSubmit} isLoading={isSubmitting}>
            Check Eligibility
          </Button>
        )}
      </div>
    </Card>
  );
}
