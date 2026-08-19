-- PostgreSQL Schema for Pump & Solar Sizing Application (Stage 2)
-- Database design preserves manufacturer data integrity and supports deterministic calculations.

-- Drop existing tables if re-initializing schema
DROP TABLE IF EXISTS pump_curves CASCADE;
DROP TABLE IF EXISTS pumps CASCADE;
DROP TYPE IF EXISTS electrical_phase_enum CASCADE;

-- Create Enum Type for Electrical Phase Configuration
CREATE TYPE electrical_phase_enum AS ENUM ('1PH', '3PH', '1PH_3PH');

-- Table 1: Pumps Specifications & Motor Data
CREATE TABLE pumps (
    pump_id VARCHAR(50) PRIMARY KEY,                       -- Lowercase canonical ID (e.g. 'ds02-09')
    pump_name VARCHAR(100) NOT NULL,                        -- Commercial model name (e.g. 'dayliff ds2/9')
    motor_kw NUMERIC(5, 2) NOT NULL CHECK (motor_kw > 0),   -- Motor power rating in kW
    max_depth_m NUMERIC(6, 2) NOT NULL CHECK (max_depth_m > 0), -- Maximum submersion depth in meters
    phase_option electrical_phase_enum NOT NULL,            -- Phase configuration enum
    flc_1ph_a NUMERIC(5, 2) NULL CHECK (flc_1ph_a IS NULL OR flc_1ph_a > 0), -- Full load current 1x240V (A)
    flc_3ph_a NUMERIC(5, 2) NULL CHECK (flc_3ph_a IS NULL OR flc_3ph_a > 0), -- Full load current 3x415V (A)
    discharge_size_in NUMERIC(4, 2) NOT NULL CHECK (discharge_size_in > 0), -- Discharge size in inches
    raw_pump_id VARCHAR(50) NOT NULL,                       -- Original extracted string for traceability
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraint: Electrical current validation against phase configuration
    CONSTRAINT chk_electrical_currents CHECK (
        (phase_option = '1PH' AND flc_1ph_a IS NOT NULL) OR
        (phase_option = '3PH' AND flc_3ph_a IS NOT NULL) OR
        (phase_option = '1PH_3PH' AND (flc_1ph_a IS NOT NULL OR flc_3ph_a IS NOT NULL))
    )
);

-- Table 2: Discrete Performance Curve Points
CREATE TABLE pump_curves (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pump_id VARCHAR(50) NOT NULL REFERENCES pumps(pump_id) ON DELETE CASCADE,
    flow_m3h NUMERIC(6, 2) NOT NULL CHECK (flow_m3h >= 0),                 -- Volumetric flow rate in m3/h
    head_m NUMERIC(6, 2) NOT NULL CHECK (head_m >= 0),                     -- Total dynamic head in meters
    efficiency_percent NUMERIC(5, 2) NOT NULL CHECK (efficiency_percent >= 0 AND efficiency_percent <= 100), -- Efficiency %
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraint: Each pump has a unique curve point at a specific flow rate
    CONSTRAINT uq_pump_flow_point UNIQUE (pump_id, flow_m3h)
);

-- Recommended Indexes for Performance & Calculations
CREATE INDEX idx_pumps_motor_kw ON pumps(motor_kw);
CREATE INDEX idx_pumps_phase_option ON pumps(phase_option);
CREATE INDEX idx_pumps_discharge_size ON pumps(discharge_size_in);
CREATE INDEX idx_pump_curves_pump_flow ON pump_curves(pump_id, flow_m3h);
CREATE INDEX idx_pump_curves_head ON pump_curves(head_m);
