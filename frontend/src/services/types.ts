export type ApplicationType = 'borehole' | 'well';

export interface RecommendationRequest {
  application_type: ApplicationType;
  yield_m3h?: number;
  pwl_m?: number;
  psd_m?: number;
  static_head_m?: number;
  customer_requested_flow_m3h?: number;
  delivery_distance_m?: number;
  destination_elevation_m?: number;
  default_pump_family?: string;
}

export interface HydraulicResult {
  static_head_m: number;
  riser_length_m: number;
  riser_friction_m: number;
  delivery_length_m: number;
  delivery_friction_m: number;
  total_dynamic_head_m: number;
  riser_pipe_quantity: number;
  standard_riser_length_m: number;
  riser_material: string;
  delivery_material: string;
  pipe_diameter_in: number;
  velocity_m_s: number;
}

export interface RecommendedPump {
  pump_id: string;
  pump_name: string;
  motor_kw: number;
  max_depth_m: number;
  phase_option: string;
  flc_1ph_a?: number;
  flc_3ph_a?: number;
  discharge_size_in: number;
  design_flow_m3h: number;
  is_depth_suitable: boolean;
  is_in_curve_range: boolean;
  is_head_suitable: boolean;
  is_viable: boolean;
  required_tdh_m: number;
  pump_head_at_design_flow_m: number;
  head_margin_m: number;
  operating_efficiency_percent: number;
  bep_flow_m3h: number;
  bep_efficiency_percent: number;
  suitability_score: number;
  hydraulic_result?: HydraulicResult;
}

export interface RejectionSummary {
  total_candidates_evaluated: number;
  viable_candidates_count: number;
  rejected_depth_exceeded: number;
  rejected_out_of_range: number;
  rejected_insufficient_head: number;
  rejected_inappropriate_flow_class: number;
  reason?: string;
}

export interface RecommendationResponse {
  status: string;
  application_type: string;
  design_flow_m3h?: number;
  abstraction_status?: string;
  yield_m3h?: number;
  pwl_m?: number;
  psd_m?: number;
  static_head_m?: number;
  destination_elevation_m?: number;
  delivery_distance_m?: number;
  warnings: string[];
  error_message?: string;
  recommended_pump?: RecommendedPump;
  alternatives: RecommendedPump[];
  rejection_summary?: RejectionSummary;
}

export interface SourceCitation {
  document: string;
  pump_family?: string;
  page?: number;
  chunk_snippet?: string;
}

export interface ExplainRequest {
  pump_id: string;
  application_type: string;
  design_flow_m3h: number;
  tdh_m: number;
  pump_head_m?: number;
  efficiency_percent?: number;
  head_margin_m?: number;
  yield_m3h?: number;
  abstraction_status?: string;
}

export interface ExplainResponse {
  answer: string;
  pump_id: string;
  pump_family: string;
  sources: SourceCitation[];
}

export interface AskRequest {
  question: string;
  pump_id?: string;
}

export interface AskResponse {
  answer: string;
  pump_id?: string;
  sources: SourceCitation[];
}

export interface HealthCheckResponse {
  status: string;
  database: string;
}
