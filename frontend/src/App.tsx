import React, { useState } from 'react';
import { AppHeader } from './components/layout/AppHeader';
import { AppFooter } from './components/layout/AppFooter';
import { HeroSection } from './components/landing/HeroSection';
import { ValuePropsSection } from './components/landing/ValuePropsSection';
import { ApplicationSelector } from './components/workspace/ApplicationSelector';
import { BoreholeForm } from './components/workspace/BoreholeForm';
import { WellForm } from './components/workspace/WellForm';
import { RecommendedCard } from './components/results/RecommendedCard';
import { AlternativeCard } from './components/results/AlternativeCard';
import { HydraulicResults } from './components/results/HydraulicResults';
import { EngineeringSummary } from './components/results/EngineeringSummary';
import { RejectionSummaryCard } from './components/results/RejectionSummary';
import { AIExplanationSection } from './components/ai/AIExplanationSection';
import { TechnicalQAModal } from './components/ai/TechnicalQAModal';
import { FutureAssistantModal } from './components/ai/FutureAssistantModal';
import { LoadingOverlay } from './components/common/LoadingOverlay';
import { ErrorAlert } from './components/common/ErrorAlert';
import type {
  ApplicationType,
  RecommendationRequest,
  RecommendationResponse,
  ExplainResponse,
} from './services/types';
import { api } from './services/api';
import { ArrowRight, RefreshCw, Calculator, Compass } from 'lucide-react';

export function App() {
  // Navigation State
  const [activeTab, setActiveTab] = useState<'landing' | 'sizing' | 'results' | 'engineering'>('landing');

  // Application Sizing Form State
  const [applicationType, setApplicationType] = useState<ApplicationType>('borehole');
  const [formData, setFormData] = useState<Partial<RecommendationRequest>>({
    application_type: 'borehole',
    yield_m3h: 12.0,
    pwl_m: 45.0,
    psd_m: 60.0,
    customer_requested_flow_m3h: 10.0,
    delivery_distance_m: 150.0,
    destination_elevation_m: 15.0,
    static_head_m: 35.0,
    default_pump_family: 'DSD',
  });

  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  // Recommendation Submission State
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [recommendationResponse, setRecommendationResponse] = useState<RecommendationResponse | null>(null);
  const [recommendationError, setRecommendationError] = useState<string | null>(null);

  // AI Explanation State
  const [isExplaining, setIsExplaining] = useState(false);
  const [explanationResponse, setExplanationResponse] = useState<ExplainResponse | null>(null);
  const [explanationError, setExplanationError] = useState<string | null>(null);

  // Modals
  const [isQAModalOpen, setIsQAModalOpen] = useState(false);
  const [isAssistantModalOpen, setIsAssistantModalOpen] = useState(false);

  // Update Form Handlers
  const handleFormChange = (updates: Partial<RecommendationRequest>) => {
    setFormData((prev) => ({ ...prev, ...updates }));
    // Clear errors when modified
    if (Object.keys(formErrors).length > 0) {
      setFormErrors({});
    }
  };

  const handleApplicationTypeChange = (app: ApplicationType) => {
    setApplicationType(app);
    setFormData((prev) => ({
      ...prev,
      application_type: app,
    }));
    setFormErrors({});
  };

  // Frontend Input Validation
  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (applicationType === 'borehole') {
      if (!formData.yield_m3h || formData.yield_m3h <= 0) {
        errors.yield_m3h = 'Borehole yield must be strictly positive (> 0 m³/h).';
      }
      if (formData.pwl_m === undefined || formData.pwl_m < 0) {
        errors.pwl_m = 'Pumping Water Level (PWL) must be non-negative (>= 0 m).';
      }
      if (!formData.psd_m || formData.psd_m <= 0) {
        errors.psd_m = 'Pump Setting Depth (PSD) must be strictly positive (> 0 m).';
      } else if (formData.pwl_m !== undefined && formData.psd_m < formData.pwl_m) {
        errors.psd_m = `Pump Setting Depth (${formData.psd_m}m) cannot be shallower than Pumping Water Level (${formData.pwl_m}m).`;
      }
    } else if (applicationType === 'well') {
      if (formData.static_head_m === undefined || formData.static_head_m < 0) {
        errors.static_head_m = 'Static Head must be non-negative (>= 0 m).';
      }
    }

    if (formData.customer_requested_flow_m3h !== undefined && formData.customer_requested_flow_m3h !== null) {
      if (formData.customer_requested_flow_m3h <= 0) {
        errors.customer_requested_flow_m3h = 'Requested flow must be strictly positive (> 0 m³/h).';
      }
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Submit Sizing Request to FastAPI Backend
  const handleSubmitSizing = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();

    if (!validateForm()) return;

    setIsSubmitting(true);
    setRecommendationError(null);
    setRecommendationResponse(null);
    setExplanationResponse(null);
    setExplanationError(null);

    const payload: RecommendationRequest = {
      application_type: applicationType,
      customer_requested_flow_m3h: formData.customer_requested_flow_m3h || undefined,
      delivery_distance_m: formData.delivery_distance_m || 0.0,
      destination_elevation_m: formData.destination_elevation_m || 0.0,
    };

    if (applicationType === 'borehole') {
      payload.yield_m3h = formData.yield_m3h;
      payload.pwl_m = formData.pwl_m;
      payload.psd_m = formData.psd_m;
    } else {
      payload.static_head_m = formData.static_head_m;
      payload.default_pump_family = formData.default_pump_family || 'DSD';
    }

    try {
      const res = await api.getRecommendation(payload);
      setRecommendationResponse(res);
      setActiveTab('results');

      if (!res.recommended_pump) {
        setRecommendationError(
          res.error_message ||
            'No suitable pump was found for these operating conditions. Try adjusting the required flow or reviewing installation parameters.'
        );
      }
    } catch (err: any) {
      setRecommendationError(
        err.message || 'An unexpected error occurred while communicating with the sizing backend.'
      );
      setActiveTab('results');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Trigger AI Explanation
  const handleRequestExplanation = async () => {
    if (!recommendationResponse?.recommended_pump) return;

    const p = recommendationResponse.recommended_pump;
    setIsExplaining(true);
    setExplanationError(null);

    try {
      const res = await api.getAIExplanation({
        pump_id: p.pump_id,
        application_type: recommendationResponse.application_type,
        design_flow_m3h: p.design_flow_m3h,
        tdh_m: p.required_tdh_m,
        pump_head_m: p.pump_head_at_design_flow_m,
        efficiency_percent: p.operating_efficiency_percent,
        head_margin_m: p.head_margin_m,
        yield_m3h: recommendationResponse.yield_m3h || undefined,
        abstraction_status: recommendationResponse.abstraction_status || 'SUSTAINABLE',
      });
      setExplanationResponse(res);
    } catch (err: any) {
      setExplanationError(err.message || 'Failed to generate AI technical explanation.');
    } finally {
      setIsExplaining(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-slate-950">
      {/* Header */}
      <AppHeader
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        hasResults={!!recommendationResponse?.recommended_pump}
        onOpenQAModal={() => setIsQAModalOpen(true)}
        onOpenAssistantModal={() => setIsAssistantModalOpen(true)}
      />

      {/* Main Workspace Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* TAB 1: LANDING OVERVIEW */}
        {activeTab === 'landing' && (
          <div className="space-y-12 animate-fade-in">
            <HeroSection
              onStartSizing={() => setActiveTab('sizing')}
              onLearnMore={() => setActiveTab('engineering')}
            />
            <ValuePropsSection onStartSizing={() => setActiveTab('sizing')} />
          </div>
        )}

        {/* TAB 2: PUMP SIZING WORKSPACE */}
        {activeTab === 'sizing' && (
          <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
            <ApplicationSelector
              selectedApp={applicationType}
              onSelectApp={handleApplicationTypeChange}
            />

            {/* Main Form Container */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl relative">
              <div className="flex items-center justify-between pb-6 mb-6 border-b border-slate-800">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 flex items-center justify-center">
                    <Calculator className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-slate-100 uppercase tracking-tight">
                      {applicationType} Hydraulic Inputs
                    </h3>
                    <p className="text-xs text-slate-400">
                      Enter field measurements to compute Total Dynamic Head & pump curve duty point.
                    </p>
                  </div>
                </div>
              </div>

              {/* Dynamic Forms */}
              <form onSubmit={handleSubmitSizing}>
                {applicationType === 'borehole' ? (
                  <BoreholeForm
                    formData={formData}
                    onChange={handleFormChange}
                    errors={formErrors}
                  />
                ) : (
                  <WellForm
                    formData={formData}
                    onChange={handleFormChange}
                    errors={formErrors}
                  />
                )}

                {/* Submit Primary CTA */}
                <div className="mt-8 pt-6 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
                  <span className="text-xs text-slate-400">
                    Calculations follow Hazen-Williams pipe friction & ISO 9906 standards.
                  </span>

                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="w-full sm:w-auto px-8 py-4 rounded-xl bg-gradient-to-r from-cyan-500 via-blue-600 to-blue-700 hover:from-cyan-400 hover:to-blue-600 text-white font-extrabold text-base shadow-xl shadow-cyan-500/25 flex items-center justify-center gap-3 transition-all cursor-pointer disabled:opacity-50"
                  >
                    <span>{isSubmitting ? 'Evaluating Candidates...' : 'Find Recommended Pump'}</span>
                    <ArrowRight className="w-5 h-5" />
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* TAB 3: RECOMMENDATION RESULTS */}
        {activeTab === 'results' && (
          <div className="space-y-8 animate-fade-in max-w-5xl mx-auto">
            {/* Loading Overlay */}
            {isSubmitting && <LoadingOverlay />}

            {/* Top Error Alert */}
            {recommendationError && !isSubmitting && (
              <ErrorAlert
                message={recommendationError}
                onRetry={() => setActiveTab('sizing')}
              />
            )}

            {/* Results Content */}
            {recommendationResponse && recommendationResponse.recommended_pump && !isSubmitting && (
              <div className="space-y-8">
                {/* Section Header */}
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                  <div>
                    <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-100 tracking-tight">
                      Pump Sizing Recommendation Results
                    </h2>
                    <p className="text-xs text-slate-400 mt-1">
                      Mode: <span className="text-cyan-400 uppercase font-mono-code font-bold">{recommendationResponse.application_type}</span> | Operating Design Flow: <span className="text-cyan-300 font-mono-code font-bold">{recommendationResponse.design_flow_m3h} m³/h</span>
                    </p>
                  </div>

                  <button
                    onClick={() => setActiveTab('sizing')}
                    className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs font-semibold text-slate-300 flex items-center gap-1.5 transition-colors cursor-pointer"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    <span>Recalculate</span>
                  </button>
                </div>

                {/* Primary Recommendation Card */}
                <RecommendedCard
                  recommendation={recommendationResponse}
                  onExplain={handleRequestExplanation}
                  isExplaining={isExplaining}
                />

                {/* AI Explanation Section */}
                {(explanationResponse || isExplaining || explanationError) && (
                  <AIExplanationSection
                    explanation={explanationResponse}
                    isLoading={isExplaining}
                    error={explanationError}
                    onRefresh={handleRequestExplanation}
                    pumpName={recommendationResponse.recommended_pump.pump_name}
                  />
                )}

                {/* Hydraulic Calculation Results Summary */}
                {recommendationResponse.recommended_pump.hydraulic_result && (
                  <HydraulicResults
                    hydraulic={recommendationResponse.recommended_pump.hydraulic_result}
                  />
                )}

                {/* Engineering Selection Narrative */}
                <EngineeringSummary recommendation={recommendationResponse} />

                {/* Alternatives Section */}
                {recommendationResponse.alternatives && recommendationResponse.alternatives.length > 0 && (
                  <div className="space-y-4">
                    <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                      <span>Viable Alternative Pumps</span>
                      <span className="text-xs text-slate-400 font-normal">
                        ({recommendationResponse.alternatives.length} candidate models evaluated)
                      </span>
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {recommendationResponse.alternatives.map((alt, idx) => (
                        <AlternativeCard key={alt.pump_id} pump={alt} index={idx} />
                      ))}
                    </div>
                  </div>
                )}

                {/* Rejection Audit */}
                {recommendationResponse.rejection_summary && (
                  <RejectionSummaryCard summary={recommendationResponse.rejection_summary} />
                )}
              </div>
            )}
          </div>
        )}

        {/* TAB 4: ABOUT ENGINEERING ENGINE */}
        {activeTab === 'engineering' && (
          <div className="max-w-4xl mx-auto space-y-8 animate-fade-in py-6">
            <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-8 shadow-xl space-y-6">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 flex items-center justify-center">
                  <Compass className="w-6 h-6" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-slate-100">
                    Kisima AI Hydraulic Sizing Principles
                  </h2>
                  <p className="text-xs text-slate-400">
                    Deterministic engineering calculation standard & RAG synthesis architecture.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs leading-relaxed text-slate-300">
                <div className="bg-slate-950 p-5 rounded-2xl border border-slate-800 space-y-2">
                  <h4 className="text-sm font-bold text-cyan-400">1. Total Dynamic Head (TDH)</h4>
                  <p>
                    Calculates static vertical lift combined with dynamic pipe friction losses calculated using the Hazen-Williams equation (<span className="font-mono-code text-cyan-300">C=150</span> for uPVC/HDPE standard riser pipes).
                  </p>
                </div>

                <div className="bg-slate-950 p-5 rounded-2xl border border-slate-800 space-y-2">
                  <h4 className="text-sm font-bold text-blue-400">2. Sustainable Abstraction</h4>
                  <p>
                    Protects borehole aquifers from drawdown over-pumping by enforcing continuous yield limits (max 75% for continuous solar pumping, 60% for high yield boreholes).
                  </p>
                </div>

                <div className="bg-slate-950 p-5 rounded-2xl border border-slate-800 space-y-2">
                  <h4 className="text-sm font-bold text-emerald-400">3. PostgreSQL H-Q Interpolation</h4>
                  <p>
                    Evaluates candidate pump curves stored in PostgreSQL using quadratic curve fitting to find exact head capability at duty flow and operating efficiency.
                  </p>
                </div>

                <div className="bg-slate-950 p-5 rounded-2xl border border-slate-800 space-y-2">
                  <h4 className="text-sm font-bold text-indigo-400">4. RAG PDF Datasheet Context</h4>
                  <p>
                    Queries ChromaDB vector embeddings over manufacturer datasheets to retrieve authentic specification citations without altering calculated hydraulic numbers.
                  </p>
                </div>
              </div>

              <div className="pt-4 text-center">
                <button
                  onClick={() => setActiveTab('sizing')}
                  className="px-8 py-3 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-sm shadow-md shadow-cyan-500/20 inline-flex items-center gap-2 cursor-pointer transition-all"
                >
                  <span>Start Pump Sizing Now</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <AppFooter />

      {/* Modals */}
      <TechnicalQAModal
        isOpen={isQAModalOpen}
        onClose={() => setIsQAModalOpen(false)}
        defaultPumpId={recommendationResponse?.recommended_pump?.pump_id}
      />

      <FutureAssistantModal
        isOpen={isAssistantModalOpen}
        onClose={() => setIsAssistantModalOpen(false)}
        onLaunchForm={() => setActiveTab('sizing')}
      />
    </div>
  );
}
