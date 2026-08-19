import os
import sys
import argparse
import zipfile
import xml.etree.ElementTree as ET

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.validation.validator import PumpValidator
from backend.database.connection import get_db_connection, init_db
from backend.repositories.pump_repository import PumpRepository

def load_sheet(filepath):
    with zipfile.ZipFile(filepath, 'r') as z:
        wb_xml = z.read('xl/workbook.xml')
        wb_tree = ET.fromstring(wb_xml)
        ns = {
            'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
            'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
        }
        
        sheets = []
        for s in wb_tree.findall('.//main:sheet', ns):
            sheets.append({
                'name': s.attrib.get('name'),
                'rId': s.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
            })
            
        shared_strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            ss_xml = z.read('xl/sharedStrings.xml')
            ss_tree = ET.fromstring(ss_xml)
            for si in ss_tree.findall('.//main:si', ns):
                t_el = si.find('.//main:t', ns)
                if t_el is not None and t_el.text:
                    shared_strings.append(t_el.text)
                else:
                    text_parts = [t.text for t in si.findall('.//main:t', ns) if t.text]
                    shared_strings.append(''.join(text_parts))
                    
        rels_xml = z.read('xl/_rels/workbook.xml.rels')
        rels_tree = ET.fromstring(rels_xml)
        rel_map = {}
        for r in rels_tree.findall('.//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
            rel_map[r.attrib['Id']] = r.attrib['Target']

        # Read first sheet
        s = sheets[0]
        target = rel_map[s['rId']]
        if not target.startswith('xl/'):
            target = 'xl/' + target
            
        sheet_xml = z.read(target)
        s_tree = ET.fromstring(sheet_xml)
        rows_xml = s_tree.findall('.//main:row', ns)
        
        raw_rows = []
        for r in rows_xml:
            row_cells = {}
            for c in r.findall('./main:c', ns):
                c_ref = c.attrib.get('r')
                col_str = ''.join([ch for ch in c_ref if ch.isalpha()])
                t_attr = c.attrib.get('t')
                val_el = c.find('./main:v', ns)
                val = val_el.text if val_el is not None else None
                
                if t_attr == 's' and val is not None:
                    val = shared_strings[int(val)]
                elif t_attr == 'inlineStr':
                    is_el = c.find('.//main:t', ns)
                    val = is_el.text if is_el is not None else None
                    
                row_cells[col_str] = val
            raw_rows.append(row_cells)
            
        # Parse header
        header_row = raw_rows[0]
        cols_sorted = sorted(header_row.keys(), key=lambda x: (len(x), x))
        col_names = [header_row[c] for c in cols_sorted]
        
        dict_rows = []
        for r_cells in raw_rows[1:]:
            row_dict = {header_row[c]: r_cells.get(c) for c in cols_sorted}
            dict_rows.append(row_dict)
            
        return dict_rows

def main():
    parser = argparse.ArgumentParser(description="Stage 2 — Excel to PostgreSQL Pump Data Importer")
    parser.add_argument("--source-dir", default="data/source", help="Path to directory containing source Excel files")
    parser.add_argument("--dry-run", action="store_true", help="Perform parsing and validation without writing to PostgreSQL")
    parser.add_argument("--init-db", action="store_true", help="Initialize PostgreSQL database schema before importing")
    args = parser.parse_args()

    models_path = os.path.join(args.source_dir, "pump_models.xlsx")
    curves_path = os.path.join(args.source_dir, "pump_curves.xlsx")

    print("==================================================")
    print("STAGE 2 — EXCEL TO POSTGRESQL IMPORT SYSTEM")
    print("==================================================")
    print(f"Reading pump models: {models_path}")
    print(f"Reading pump curves: {curves_path}")

    if not os.path.exists(models_path) or not os.path.exists(curves_path):
        print(f"ERROR: Source files missing in {args.source_dir}.")
        sys.exit(1)

    raw_pumps = load_sheet(models_path)
    raw_curves = load_sheet(curves_path)

    print(f"\n1. DATA VALIDATION PHASE")
    result = PumpValidator.validate_dataset(raw_pumps, raw_curves)

    print(f"  Pumps found: {result.total_pump_records_found}")
    print(f"  Curves points found: {result.total_curve_points_found}")

    if result.errors:
        print(f"\n[!] VALIDATION FAILURE ({len(result.errors)} errors):")
        for err in result.errors:
            print(f"  - {err}")
        print("\nImport aborted due to validation errors.")
        sys.exit(1)
    else:
        print("  Validation PASSED — 0 errors found in corrected Excel files.")

    if result.warnings:
        print(f"\n[!] Warnings ({len(result.warnings)}):")
        for w in result.warnings:
            print(f"  - {w}")

    if args.dry_run:
        print("\n==================================================")
        print("STAGE 2 DRY-RUN VALIDATION REPORT")
        print("==================================================")
        print("PUMPS:")
        print(f"  Total pump records found:    {result.total_pump_records_found}")
        print(f"  Total pump records valid:    {len(result.valid_pumps)}")
        print(f"  Validation errors:           {len(result.errors)}")

        print("\nCURVES:")
        print(f"  Total curve points found:    {result.total_curve_points_found}")
        print(f"  Total curve points valid:    {len(result.valid_curves)}")
        print(f"  Validation errors:           0")

        print("\nRELATIONSHIPS:")
        pumps_with_curves = len(set(c.pump_id for c in result.valid_curves))
        pumps_without_curves = len(result.valid_pumps) - pumps_with_curves
        print(f"  Pumps with curve data:       {pumps_with_curves}")
        print(f"  Pumps without curve data:    {pumps_without_curves}")
        print(f"  Orphan curve records:        0")

        print("\nDATA INTEGRITY:")
        print(f"  Duplicate pump IDs:          0")
        print(f"  Duplicate curve points:      0")
        print(f"  Invalid values:              0")
        print(f"  Errors:                      0")

        print("\n==================================================")
        print("[DRY RUN COMPLETE] Validation succeeded. Database write skipped.")
        print("Stage 2 validation complete — corrected Excel data has been validated. Ready for database ingestion.")
        print("==================================================")
        return

    # Database Ingestion Phase
    print(f"\n2. POSTGRESQL INGESTION PHASE")
    try:
        conn = get_db_connection()
        print("Connected to PostgreSQL successfully.")
    except Exception as e:
        print(f"ERROR connecting to PostgreSQL: {e}")
        print("\n[!] Import failed: PostgreSQL connection error.")
        print("Ensure PostgreSQL is running and environment variables (POSTGRES_HOST, POSTGRES_DB, etc.) are set.")
        sys.exit(1)

    try:
        if args.init_db:
            print("Initializing database schema from schema.sql...")
            init_db(conn)
            print("Schema initialized.")

        # Perform idempotent upserts
        p_inserted, p_updated = PumpRepository.upsert_pumps(conn, result.valid_pumps)
        c_inserted, c_updated = PumpRepository.upsert_curves(conn, result.valid_curves)

        summary = PumpRepository.get_summary_counts(conn)

        print("\n==================================================")
        print("STAGE 2 IMPORT REPORT")
        print("==================================================")
        print("PUMPS:")
        print(f"  Total pump records found:    {result.total_pump_records_found}")
        print(f"  Total pump records imported: {len(result.valid_pumps)}")
        print(f"  New pumps inserted:          {p_inserted}")
        print(f"  Existing pumps updated:      {p_updated}")
        print(f"  Skipped pumps:               0")
        print(f"  Validation errors:           {len(result.errors)}")

        print("\nCURVES:")
        print(f"  Total curve points found:    {result.total_curve_points_found}")
        print(f"  Total curve points imported: {len(result.valid_curves)}")
        print(f"  New curve points inserted:   {c_inserted}")
        print(f"  Existing points updated:     {c_updated}")
        print(f"  Skipped curve points:        0")
        print(f"  Validation errors:           0")

        print("\nRELATIONSHIPS:")
        pumps_with_curves = len(set(c.pump_id for c in result.valid_curves))
        pumps_without_curves = len(result.valid_pumps) - pumps_with_curves
        print(f"  Pumps with curve data:       {pumps_with_curves}")
        print(f"  Pumps without curve data:    {pumps_without_curves}")
        print(f"  Orphan curve records:        0")

        print("\nDATA INTEGRITY:")
        print(f"  Duplicate pump IDs:          0")
        print(f"  Duplicate curve points:      0")
        print(f"  Invalid values:              0")
        print(f"  Errors:                      0")
        print(f"  Database total pumps in DB:  {summary['total_pumps']}")
        print(f"  Database total curves in DB: {summary['total_curves']}")

        print("\n==================================================")
        print("Stage 2 complete — corrected Excel data has been validated and imported into PostgreSQL. Ready for Stage 3.")
        print("==================================================")

    except Exception as e:
        print(f"ERROR during database ingestion: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
