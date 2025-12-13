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
  const [customerId, setCustomerId] = useState("");
  const [aiDecision, setAiDecision] = useState<any>(null);
  const [isLoadingDecision, setIsLoadingDecision] = useState(false);
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
      if (!data[field] || (typeof data[field] === "string" && data[field].trim() === "")) {
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

      // Store customer ID and show result screen immediately
      const custId = result.customerId;
      setCustomerId(custId);
      setIsSubmitted(true);
      setIsLoadingDecision(true);

      // Poll for AI decision in the background
      const pollDecision = async () => {
        try {
          const maxAttempts = 30; // 30 attempts = 1 minute
          let attempts = 0;

          const poll = async (): Promise<void> => {
            if (attempts >= maxAttempts) {
              console.log('AI processing timeout - showing manual review message');
              setAiDecision({
                decision: 'MANUAL_REVIEW',
                risk_score: 50,
                confidence_score: 0.5,
                reasoning: 'AI processing is taking longer than expected. Our team will review your application manually.',
                conditions: ['Processing timeout - manual review required']
              });
              setIsLoadingDecision(false);
              return;
            }

            attempts++;

            try {
              // Check status first
              const statusRes = await fetch(`http://localhost:8000/api/status/${custId}`);
              if (statusRes.ok) {
                const statusData = await statusRes.json();
                
                if (statusData.status === 'completed') {
                  // Fetch the actual decision
                  const decisionRes = await fetch(`http://localhost:8000/api/result/${custId}`);
                  if (decisionRes.ok) {
                    const decision = await decisionRes.json();
                    setAiDecision(decision);
                    setIsLoadingDecision(false);
                    return;
                  }
                } else if (statusData.status === 'failed') {
                  console.error('AI processing failed:', statusData.error);
                  setAiDecision({
                    decision: 'MANUAL_REVIEW',
                    risk_score: 50,
                    confidence_score: 0.5,
                    reasoning: 'AI processing encountered an error. Our team will review your application manually.',
                    conditions: ['AI processing error - manual review required']
                  });
                  setIsLoadingDecision(false);
                  return;
                }
              }

              // Continue polling
              setTimeout(poll, 2000); // Poll every 2 seconds
            } catch (error) {
              console.error('Error polling decision:', error);
              setTimeout(poll, 2000);
            }
          };

          await poll();
        } catch (error) {
          console.error('Error in polling logic:', error);
          setAiDecision({
            decision: 'MANUAL_REVIEW',
            risk_score: 50,
            confidence_score: 0.5,
            reasoning: 'Unable to retrieve AI decision. Our team will review your application manually.',
            conditions: ['Network error - manual review required']
          });
          setIsLoadingDecision(false);
        }
      };

      // Start polling
      pollDecision();
    } catch (error) {
      console.error('Error submitting application:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to submit application. Please try again.';
      alert(`Error: ${errorMessage}\n\nPlease ensure:\n1. Cloud SQL Proxy is running\n2. Backend services are available\n3. All required fields are filled`);
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setData(INITIAL_DATA);
    setStep(1);
    setIsSubmitted(false);
    setCustomerId("");
    setAiDecision(null);
    setIsLoadingDecision(false);
    setErrors({});
  };

  if (isSubmitted) {
    return (
      <Card className="w-full max-w-lg mx-auto mt-10">
        <Result 
          customerId={customerId} 
          aiDecision={aiDecision} 
          isLoading={isLoadingDecision}
          onReset={handleReset} 
        />
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
