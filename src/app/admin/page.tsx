"use client";

import { useState, useEffect } from "react";
import { Navbar } from "@/components/layout/Navbar";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import {
  FileText,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  RefreshCw,
  Eye,
  TrendingUp,
  DollarSign,
  User
} from "lucide-react";

interface Application {
  customer_id: string;
  application_status: string;
  eligibility_score: number | null;
  created_at: string;
  first_name: string;
  last_name: string;
  loan_amount: number;
  loan_purpose: string;
}

interface ApplicationDetails extends Application {
  personal_id?: string;
  gender?: string;
  birth_year?: string;
  phone?: string;
  address?: string;
  education_level?: string;
  university?: string;
  employment_status?: string;
  company_name?: string;
  monthly_salary?: number;
  experience_years?: number;
  loan_duration?: number;
  additional_info?: string;
}

interface AIDecision {
  decision: string;
  confidence_score: number;
  risk_score: number;
  loan_amount?: number;
  interest_rate?: number;
  loan_duration?: number;
  conditions: string[];
  reasoning: string;
}

export default function AdminPage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [selectedApp, setSelectedApp] = useState<ApplicationDetails | null>(null);
  const [aiDecision, setAiDecision] = useState<AIDecision | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingDecision, setIsLoadingDecision] = useState(false);
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    approved: 0,
    rejected: 0,
    manualReview: 0,
    totalLoanAmount: 0
  });

  useEffect(() => {
    fetchApplications();
  }, []);

  const fetchApplications = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/loan-application');
      if (response.ok) {
        const data = await response.json();
        setApplications(data.applications || []);
        calculateStats(data.applications || []);
      }
    } catch (error) {
      console.error('Error fetching applications:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const calculateStats = (apps: Application[]) => {
    const stats = {
      total: apps.length,
      pending: 0,
      approved: 0,
      rejected: 0,
      manualReview: 0,
      totalLoanAmount: 0
    };

    apps.forEach(app => {
      stats.totalLoanAmount += app.loan_amount || 0;
      switch (app.application_status?.toLowerCase()) {
        case 'pending':
          stats.pending++;
          break;
        case 'approved':
          stats.approved++;
          break;
        case 'rejected':
          stats.rejected++;
          break;
        case 'manual_review':
          stats.manualReview++;
          break;
      }
    });

    setStats(stats);
  };

  const fetchApplicationDetails = async (customerId: string) => {
    try {
      const response = await fetch(`/api/loan-application?customerId=${customerId}`);
      if (response.ok) {
        const data = await response.json();
        setSelectedApp(data.application);
        // Don't automatically fetch AI decision - user must click button
        setAiDecision(null); // Reset AI decision when selecting new app
      }
    } catch (error) {
      console.error('Error fetching application details:', error);
    }
  };

  const fetchAIDecision = async (customerId: string) => {
    setIsLoadingDecision(true);
    try {
      // Check status first
      const statusRes = await fetch(`http://localhost:8000/api/status/${customerId}`);
      if (statusRes.ok) {
        const statusData = await statusRes.json();
        if (statusData.status === 'completed' && statusData.result) {
          setAiDecision({
            decision: statusData.result.decision,
            confidence_score: statusData.result.confidenceScore ?? statusData.result.confidence_score,
            risk_score: statusData.result.riskScore ?? statusData.result.risk_score,
            loan_amount: statusData.result.approvedAmount ?? statusData.result.loan_amount,
            interest_rate: statusData.result.interestRate ?? statusData.result.interest_rate,
            conditions: statusData.result.conditions || [],
            reasoning: statusData.result.reasoning
          });
        } else {
          // Try to fetch result directly
          const resultRes = await fetch(`http://localhost:8000/api/result/${customerId}`);
          if (resultRes.ok) {
            const result = await resultRes.json();
            setAiDecision(result);
          }
        }
      }
    } catch (error) {
      console.error('Error fetching AI decision:', error);
    } finally {
      setIsLoadingDecision(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'approved':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'rejected':
        return <XCircle className="w-5 h-5 text-red-400" />;
      case 'manual_review':
        return <AlertCircle className="w-5 h-5 text-yellow-400" />;
      default:
        return <Clock className="w-5 h-5 text-slate-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'approved':
        return 'bg-green-500/20 text-green-300 border-green-500/50';
      case 'rejected':
        return 'bg-red-500/20 text-red-300 border-red-500/50';
      case 'manual_review':
        return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/50';
      default:
        return 'bg-slate-500/20 text-slate-300 border-slate-500/50';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(amount);
  };

  return (
    <div className="min-h-screen bg-[#030712] text-slate-200">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Admin Dashboard</h1>
            <p className="text-slate-400">Credit Officer Portal - Loan Application Management</p>
          </div>
          <Button onClick={fetchApplications} variant="outline" className="gap-2">
            <RefreshCw className="w-4 h-4" />
            Refresh
          </Button>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Card className="bg-white/5 border-white/10">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm mb-1">Total Applications</p>
                <p className="text-3xl font-bold text-white">{stats.total}</p>
              </div>
              <FileText className="w-8 h-8 text-indigo-400" />
            </div>
          </Card>

          <Card className="bg-white/5 border-white/10">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm mb-1">Pending Review</p>
                <p className="text-3xl font-bold text-yellow-300">{stats.pending}</p>
              </div>
              <Clock className="w-8 h-8 text-yellow-400" />
            </div>
          </Card>

          <Card className="bg-white/5 border-white/10">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm mb-1">Approved</p>
                <p className="text-3xl font-bold text-green-300">{stats.approved}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-400" />
            </div>
          </Card>

          <Card className="bg-white/5 border-white/10">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm mb-1">Total Loan Amount</p>
                <p className="text-2xl font-bold text-white">{formatCurrency(stats.totalLoanAmount)}</p>
              </div>
              <DollarSign className="w-8 h-8 text-cyan-400" />
            </div>
          </Card>
        </div>

        {/* Applications Table */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Applications List */}
          <div className="lg:col-span-2">
            <Card>
              <h2 className="text-xl font-bold text-white mb-4">Loan Applications</h2>

              {isLoading ? (
                <div className="text-center py-8 text-slate-400">Loading applications...</div>
              ) : applications.length === 0 ? (
                <div className="text-center py-8 text-slate-400">No applications found</div>
              ) : (
                <div className="space-y-3 max-h-[600px] overflow-y-auto">
                  {applications.map((app) => (
                    <div
                      key={app.customer_id}
                      className={`p-4 rounded-lg border cursor-pointer transition-all hover:bg-white/5 ${selectedApp?.customer_id === app.customer_id
                        ? 'bg-indigo-500/10 border-indigo-500/50'
                        : 'bg-white/5 border-white/10'
                        }`}
                      onClick={() => fetchApplicationDetails(app.customer_id)}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <User className="w-4 h-4 text-slate-400" />
                            <span className="font-semibold text-white">
                              {app.first_name} {app.last_name}
                            </span>
                          </div>
                          <p className="text-sm text-slate-400">
                            {app.customer_id.substring(0, 8)}...
                          </p>
                        </div>
                        <div className={`px-3 py-1 rounded-full border text-xs font-medium flex items-center gap-1 ${getStatusColor(app.application_status)}`}>
                          {getStatusIcon(app.application_status)}
                          {app.application_status}
                        </div>
                      </div>
                      <div className="flex items-center justify-between mt-3 pt-3 border-t border-white/10">
                        <div>
                          <p className="text-xs text-slate-400">Loan Amount</p>
                          <p className="text-sm font-semibold text-white">{formatCurrency(app.loan_amount)}</p>
                        </div>
                        <div>
                          <p className="text-xs text-slate-400">Purpose</p>
                          <p className="text-sm text-slate-300">{app.loan_purpose}</p>
                        </div>
                        <div>
                          <p className="text-xs text-slate-400">Applied</p>
                          <p className="text-sm text-slate-300">{formatDate(app.created_at)}</p>
                        </div>
                      </div>
                      {app.eligibility_score !== null && (
                        <div className="mt-2 pt-2 border-t border-white/10">
                          <div className="flex items-center gap-2">
                            <TrendingUp className="w-4 h-4 text-indigo-400" />
                            <span className="text-xs text-slate-400">Eligibility Score:</span>
                            <span className="text-sm font-semibold text-indigo-300">{app.eligibility_score}</span>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>

          {/* Application Details Panel */}
          <div className="lg:col-span-1">
            {selectedApp ? (
              <Card className="sticky top-4">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold text-white">Application Details</h2>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSelectedApp(null)}
                  >
                    ×
                  </Button>
                </div>

                <div className="space-y-4 max-h-[600px] overflow-y-auto">
                  {/* Customer Info */}
                  <div>
                    <h3 className="text-sm font-semibold text-slate-300 mb-2">Customer Information</h3>
                    <div className="space-y-2 text-sm">
                      <div>
                        <span className="text-slate-400">Name:</span>
                        <span className="ml-2 text-white">{selectedApp.first_name} {selectedApp.last_name}</span>
                      </div>
                      {selectedApp.personal_id && (
                        <div>
                          <span className="text-slate-400">ID:</span>
                          <span className="ml-2 text-white">{selectedApp.personal_id}</span>
                        </div>
                      )}
                      {selectedApp.phone && (
                        <div>
                          <span className="text-slate-400">Phone:</span>
                          <span className="ml-2 text-white">{selectedApp.phone}</span>
                        </div>
                      )}
                      {selectedApp.address && (
                        <div>
                          <span className="text-slate-400">Address:</span>
                          <span className="ml-2 text-white">{selectedApp.address}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Employment Info */}
                  {(selectedApp.employment_status || selectedApp.monthly_salary) && (
                    <div>
                      <h3 className="text-sm font-semibold text-slate-300 mb-2">Employment</h3>
                      <div className="space-y-2 text-sm">
                        {selectedApp.employment_status && (
                          <div>
                            <span className="text-slate-400">Status:</span>
                            <span className="ml-2 text-white capitalize">{selectedApp.employment_status}</span>
                          </div>
                        )}
                        {selectedApp.company_name && (
                          <div>
                            <span className="text-slate-400">Company:</span>
                            <span className="ml-2 text-white">{selectedApp.company_name}</span>
                          </div>
                        )}
                        {selectedApp.monthly_salary && (
                          <div>
                            <span className="text-slate-400">Salary:</span>
                            <span className="ml-2 text-white">{formatCurrency(selectedApp.monthly_salary)}/month</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Loan Details */}
                  <div>
                    <h3 className="text-sm font-semibold text-slate-300 mb-2">Loan Details</h3>
                    <div className="space-y-2 text-sm">
                      <div>
                        <span className="text-slate-400">Amount:</span>
                        <span className="ml-2 text-white font-semibold">{formatCurrency(selectedApp.loan_amount)}</span>
                      </div>
                      {selectedApp.loan_duration && (
                        <div>
                          <span className="text-slate-400">Duration:</span>
                          <span className="ml-2 text-white">{selectedApp.loan_duration} months</span>
                        </div>
                      )}
                      <div>
                        <span className="text-slate-400">Purpose:</span>
                        <span className="ml-2 text-white">{selectedApp.loan_purpose}</span>
                      </div>
                    </div>
                  </div>

                  {/* AI Decision */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-sm font-semibold text-slate-300">AI Decision</h3>
                      {!aiDecision && !isLoadingDecision && (
                        <Button
                          onClick={() => fetchAIDecision(selectedApp.customer_id)}
                          size="sm"
                          variant="outline"
                          className="text-xs"
                        >
                          Load AI Review
                        </Button>
                      )}
                    </div>
                    {isLoadingDecision ? (
                      <div className="text-sm text-slate-400">Loading decision...</div>
                    ) : aiDecision ? (
                      <div className="space-y-3">
                        <div className={`p-3 rounded-lg border ${getStatusColor(aiDecision.decision)}`}>
                          <div className="flex items-center gap-2 mb-2">
                            {getStatusIcon(aiDecision.decision)}
                            <span className="font-semibold uppercase">{aiDecision.decision}</span>
                          </div>
                          <div className="space-y-1 text-xs">
                            <div className="flex justify-between">
                              <span className="text-slate-400">Risk Score:</span>
                              <span className="text-white">{aiDecision.risk_score}/100</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-slate-400">Confidence:</span>
                              <span className="text-white">{(aiDecision.confidence_score * 100).toFixed(1)}%</span>
                            </div>
                            {aiDecision.loan_amount && (
                              <div className="flex justify-between">
                                <span className="text-slate-400">Approved Amount:</span>
                                <span className="text-white font-semibold">{formatCurrency(aiDecision.loan_amount)}</span>
                              </div>
                            )}
                            {aiDecision.interest_rate && (
                              <div className="flex justify-between">
                                <span className="text-slate-400">Interest Rate:</span>
                                <span className="text-white">{aiDecision.interest_rate}%</span>
                              </div>
                            )}
                          </div>
                        </div>
                        <div>
                          <p className="text-xs text-slate-400 mb-1">Reasoning:</p>
                          <p className="text-xs text-slate-300 bg-white/5 p-2 rounded">{aiDecision.reasoning}</p>
                        </div>
                        {aiDecision.conditions && aiDecision.conditions.length > 0 && (
                          <div>
                            <p className="text-xs text-slate-400 mb-1">Conditions:</p>
                            <ul className="text-xs text-slate-300 space-y-1">
                              {aiDecision.conditions.map((condition, idx) => (
                                <li key={idx} className="bg-white/5 p-2 rounded">• {condition}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="text-sm text-slate-400">Click "Load AI Review" to see the AI analysis</div>
                    )}
                  </div>
                </div>
              </Card>
            ) : (
              <Card>
                <div className="text-center py-8 text-slate-400">
                  <Eye className="w-12 h-12 mx-auto mb-3 text-slate-600" />
                  <p>Select an application to view details</p>
                </div>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

