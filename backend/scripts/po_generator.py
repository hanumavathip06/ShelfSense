import sys
import os
import math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models import Product, Supplier, PurchaseOrder, PurchaseOrderItem, SystemSetting, ForecastResult

def get_setting(key, default):
    setting = SystemSetting.query.get(key)
    return setting.value if setting else default

def generate_pos(dry_run=False):
    print(f"--- Starting PO Generator (Dry Run: {dry_run}) ---")
    app = create_app()
    with app.app_context():
        # Check global killswitch
        killswitch = get_setting('GLOBAL_PO_KILLSWITCH', 'False')
        if killswitch.lower() == 'true':
            print("WARNING: GLOBAL_PO_KILLSWITCH is enabled. Forcing dry-run mode.")
            dry_run = True

        daily_spend_limit = float(get_setting('DAILY_SPEND_LIMIT', '10000.0'))
        
        # In a real app, this would use a complex query or join.
        products = Product.query.all()
        
        # Group by supplier
        supplier_orders = {}
        
        for product in products:
            if not product.supplier_id:
                continue
                
            supplier = Supplier.query.get(product.supplier_id)
            if not supplier:
                continue
                
            lead_time = supplier.lead_time_days or product.lead_time_days
            moq = supplier.moq or 1
            pack_size = supplier.pack_size or 1
            
            # 1. Forecast logic
            # In Phase 4, we would look up the ForecastResult over the lead_time.
            # Mocking the forecast here for demonstration.
            # Assuming average daily demand of 5 items if no ML data.
            avg_daily_demand = 5
            forecasted_demand_over_lt = avg_daily_demand * lead_time
            
            # Safety stock calculation (Z-score 1.64 for 95% service level)
            std_dev_demand = 2.0
            safety_stock = 1.64 * std_dev_demand * math.sqrt(lead_time)
            
            # Calculate total on-hand and on-order
            on_hand = product.quantity
            # Mocking on-order stock (would query PurchaseOrderItem where PO status is pending/sent)
            on_order = 0 
            
            predicted_inventory = on_hand + on_order - forecasted_demand_over_lt
            
            if predicted_inventory < safety_stock:
                # 2. Order Quantity Calculation
                raw_qty = forecasted_demand_over_lt + safety_stock - on_hand - on_order
                
                # Round to pack size and enforce MOQ
                rounded_qty = math.ceil(raw_qty / pack_size) * pack_size
                final_qty = max(rounded_qty, moq)
                
                if final_qty > 0:
                    if supplier.id not in supplier_orders:
                        supplier_orders[supplier.id] = []
                        
                    supplier_orders[supplier.id].append({
                        'product_id': product.id,
                        'product_name': product.name,
                        'qty': final_qty,
                        'unit_price': float(product.unit_price)
                    })
                    
        # 3. Create Draft POs
        total_spend_today = 0.0 # Would query DB for today's POs
        
        for supplier_id, items in supplier_orders.items():
            supplier = Supplier.query.get(supplier_id)
            po_total = sum(item['qty'] * item['unit_price'] for item in items)
            
            print(f"\\n[Supplier: {supplier.name}]")
            
            if total_spend_today + po_total > daily_spend_limit:
                print(f"  -> BLOCKED: Daily spend limit exceeded (Limit: ${daily_spend_limit}, Requested: ${total_spend_today + po_total})")
                continue
                
            # 4. Auto-send evaluation
            status = 'draft'
            if supplier.is_trusted and supplier.auto_send_orders and po_total < 5000.0:
                 status = 'approved' # Auto-approval
                 
            print(f"  -> Creating PO (Status: {status}, Total: ${po_total:.2f})")
            
            for item in items:
                print(f"    - SKU: {item['product_name']}, Qty: {item['qty']}, Cost: ${item['qty'] * item['unit_price']:.2f}")
                
            if not dry_run:
                po = PurchaseOrder(supplier_id=supplier_id, status=status, total_amount=po_total)
                db.session.add(po)
                db.session.flush()
                
                for item in items:
                    po_item = PurchaseOrderItem(
                        po_id=po.id, 
                        product_id=item['product_id'], 
                        quantity=item['qty'], 
                        unit_price=item['unit_price']
                    )
                    db.session.add(po_item)
                    
                total_spend_today += po_total
                
        if not dry_run:
            db.session.commit()
            print("\\n--- POs committed to database ---")
        else:
            print("\\n--- Dry Run Complete (No changes made) ---")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Run without committing to DB')
    args = parser.parse_args()
    
    generate_pos(dry_run=args.dry_run)
