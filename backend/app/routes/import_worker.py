import csv
import os
from datetime import datetime
from app.extensions import db
from app.models import ImportJob, Product, AuditLog

def sanitize_cell(cell_value):
    """Prevent CSV/formula injection."""
    if not isinstance(cell_value, str):
        return cell_value
    if cell_value.startswith(('=', '+', '-', '@')):
        return "'" + cell_value
    return cell_value

def process_import_job(job_id, action, app):
    """
    Background worker for processing imports.
    """
    with app.app_context():
        job = ImportJob.query.get(job_id)
        if not job:
            return
            
        if action == 'extract_headers':
            # Simulated header extraction
            pass
            
        elif action == 'commit':
            job.status = 'importing'
            job.started_at = datetime.utcnow()
            db.session.commit()
            
            # Stream-parse CSV
            if job.filename.endswith('.csv'):
                try:
                    with open(job.filename, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        batch = []
                        processed = 0
                        
                        for row in reader:
                            # Sanitize row
                            clean_row = {k: sanitize_cell(v) for k, v in row.items()}
                            
                            # Upsert logic for products
                            if job.entity_type == 'products':
                                sku = clean_row.get(job.mapping_config.get('sku', 'sku'))
                                name = clean_row.get(job.mapping_config.get('name', 'name'))
                                
                                if not sku or not name:
                                    job.error_count += 1
                                    continue
                                
                                p = Product.query.filter_by(sku=sku).first()
                                if p:
                                    if job.import_mode == 'update':
                                        p.name = name
                                        # ... update other fields mapped
                                else:
                                    p = Product(sku=sku, name=name, quantity=0)
                                    db.session.add(p)
                                    
                            processed += 1
                            if processed % 100 == 0:
                                job.processed_rows = processed
                                job.progress = min(99, int((processed / max(job.total_rows, 1)) * 100))
                                db.session.commit()
                        
                        job.processed_rows = processed
                        job.progress = 100
                        job.status = 'completed'
                        job.finished_at = datetime.utcnow()
                        
                        # Audit log
                        audit = AuditLog(
                            user_id=job.user_id,
                            action='bulk_import',
                            target_resource=job.entity_type,
                            details=f"Imported {processed} records from {job.filename}"
                        )
                        db.session.add(audit)
                        db.session.commit()
                except Exception as e:
                    job.status = 'failed'
                    db.session.commit()
            
            elif job.filename.endswith('.xlsx'):
                try:
                    import openpyxl
                    # read_only=True streams the file, drastically reducing memory footprint.
                    wb = openpyxl.load_workbook(job.filename, read_only=True, data_only=True)
                    ws = wb.active
                    
                    headers = None
                    processed = 0
                    
                    for row in ws.iter_rows(values_only=True):
                        if headers is None:
                            headers = [str(cell) if cell else f"col_{i}" for i, cell in enumerate(row)]
                            continue
                            
                        # Zip headers with row data and sanitize
                        row_dict = {headers[i]: sanitize_cell(cell) for i, cell in enumerate(row)}
                        
                        if job.entity_type == 'products':
                            sku = row_dict.get(job.mapping_config.get('sku', 'sku'))
                            name = row_dict.get(job.mapping_config.get('name', 'name'))
                            
                            if not sku or not name:
                                job.error_count += 1
                                continue
                            
                            p = Product.query.filter_by(sku=sku).first()
                            if p:
                                if job.import_mode == 'update':
                                    p.name = name
                            else:
                                p = Product(sku=sku, name=name, quantity=0)
                                db.session.add(p)
                                
                        processed += 1
                        
                        # Batch commit every 1000 rows
                        if processed % 1000 == 0:
                            job.processed_rows = processed
                            job.progress = min(99, int((processed / max(job.total_rows, 1)) * 100))
                            db.session.commit()
                            
                    job.processed_rows = processed
                    job.progress = 100
                    job.status = 'completed'
                    job.finished_at = datetime.utcnow()
                    
                    audit = AuditLog(
                        user_id=job.user_id,
                        action='bulk_import',
                        target_resource=job.entity_type,
                        details=f"Imported {processed} records from {job.filename} (Excel)"
                    )
                    db.session.add(audit)
                    db.session.commit()
                    wb.close()
                except Exception as e:
                    job.status = 'failed'
                    db.session.commit()
