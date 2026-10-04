import { useState, useCallback } from 'react';
import { UploadCloud, FileSpreadsheet, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';

type Step = 'upload' | 'mapping' | 'preview' | 'importing' | 'result';

export function ImportData() {
  const [currentStep, setCurrentStep] = useState<Step>('upload');
  const [file, setFile] = useState<File | null>(null);
  const [entityType, setEntityType] = useState('products');
  const [jobId, setJobId] = useState<number | null>(null);
  const [progress, setProgress] = useState(0);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.name.endsWith('.csv') || droppedFile.name.endsWith('.xlsx')) {
        setFile(droppedFile);
      } else {
        toast.error('Only .csv and .xlsx files are supported');
      }
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const startUpload = async () => {
    if (!file) return;
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('entity_type', entityType);

      // We'd send this to the API here
      // const res = await fetch('/api/v1/imports/upload', { ... })
      // const data = await res.json()
      // setJobId(data.job_id)
      
      toast.success('File uploaded successfully!');
      setCurrentStep('mapping');
    } catch (err) {
      toast.error('Failed to upload file');
    }
  };

  const confirmMapping = () => {
    setCurrentStep('preview');
  };

  const startImport = () => {
    setCurrentStep('importing');
    
    // Simulate real-time progress via polling
    let current = 0;
    const interval = setInterval(() => {
      current += 10;
      setProgress(current);
      if (current >= 100) {
        clearInterval(interval);
        setCurrentStep('result');
        toast.success('Data imported successfully!');
      }
    }, 500);
  };

  const reset = () => {
    setFile(null);
    setCurrentStep('upload');
    setProgress(0);
    setJobId(null);
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-primary">Bulk Import</h1>
        <div className="flex gap-2">
          <a href="/templates/products.csv" download className="text-sm text-accent hover:underline flex items-center gap-1">
            <FileSpreadsheet className="w-4 h-4" /> Product Template
          </a>
        </div>
      </div>

      <div className="bg-surface rounded-lg shadow-sm border border-border p-6">
        {/* Progress Bar Header */}
        <div className="flex items-center justify-between mb-8">
          <div className={`flex flex-col items-center ${currentStep === 'upload' ? 'text-accent' : 'text-secondary'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${currentStep === 'upload' ? 'bg-accent/20' : 'bg-background'} font-bold`}>1</div>
            <span className="text-xs mt-1">Upload</span>
          </div>
          <div className="flex-1 h-1 mx-4 bg-border">
             <div className={`h-full bg-accent transition-all duration-500 ${currentStep !== 'upload' ? 'w-full' : 'w-0'}`} />
          </div>
          <div className={`flex flex-col items-center ${currentStep === 'mapping' ? 'text-accent' : 'text-secondary'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${currentStep === 'mapping' ? 'bg-accent/20' : 'bg-background'} font-bold`}>2</div>
            <span className="text-xs mt-1">Map Columns</span>
          </div>
          <div className="flex-1 h-1 mx-4 bg-border">
             <div className={`h-full bg-accent transition-all duration-500 ${['preview', 'importing', 'result'].includes(currentStep) ? 'w-full' : 'w-0'}`} />
          </div>
          <div className={`flex flex-col items-center ${['preview', 'importing', 'result'].includes(currentStep) ? 'text-accent' : 'text-secondary'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${['preview', 'importing', 'result'].includes(currentStep) ? 'bg-accent/20' : 'bg-background'} font-bold`}>3</div>
            <span className="text-xs mt-1">Validate & Import</span>
          </div>
        </div>

        {currentStep === 'upload' && (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-secondary mb-2">Select Entity to Import</label>
              <select 
                value={entityType}
                onChange={(e) => setEntityType(e.target.value)}
                className="w-full rounded-md border border-border bg-background px-3 py-2 text-primary focus:outline-none focus:ring-2 focus:ring-accent"
              >
                <option value="products">Products</option>
                <option value="stock_movements">Stock Movements</option>
                <option value="suppliers">Suppliers</option>
              </select>
            </div>

            <div 
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              className="border-2 border-dashed border-border rounded-xl p-10 text-center hover:bg-background/50 transition-colors cursor-pointer"
            >
              <input type="file" id="fileUpload" className="hidden" accept=".csv,.xlsx" onChange={handleFileChange} />
              <label htmlFor="fileUpload" className="cursor-pointer flex flex-col items-center">
                <UploadCloud className="w-12 h-12 text-secondary mb-4" />
                <p className="text-lg font-medium text-primary mb-1">
                  {file ? file.name : 'Drag & drop a file here'}
                </p>
                <p className="text-sm text-secondary">
                  {file ? `${(file.size / 1024).toFixed(1)} KB` : 'or click to browse (.csv, .xlsx up to 50MB)'}
                </p>
              </label>
            </div>
            
            <div className="flex justify-end">
              <button 
                onClick={startUpload}
                disabled={!file}
                className="bg-accent text-white px-6 py-2 rounded-md font-medium disabled:opacity-50 hover:bg-accent/90 transition-colors"
              >
                Upload & Next
              </button>
            </div>
          </div>
        )}

        {currentStep === 'mapping' && (
          <div className="space-y-6">
            <h3 className="text-lg font-medium text-primary">Map Your Columns</h3>
            <p className="text-sm text-secondary">We've auto-detected some columns from your file. Please confirm the mapping.</p>
            
            <div className="border border-border rounded-lg overflow-hidden">
              <table className="min-w-full divide-y divide-border">
                <thead className="bg-background">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">Required Field</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">Your File Column</th>
                  </tr>
                </thead>
                <tbody className="bg-surface divide-y divide-border">
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-primary">SKU *</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary">
                      <select className="bg-background border border-border rounded p-1 w-full text-primary">
                        <option>sku_id</option>
                        <option>item_code</option>
                      </select>
                    </td>
                  </tr>
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-primary">Product Name *</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary">
                      <select className="bg-background border border-border rounded p-1 w-full text-primary">
                        <option>name</option>
                        <option>description</option>
                      </select>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <div className="flex justify-end gap-3">
              <button onClick={() => setCurrentStep('upload')} className="px-4 py-2 text-secondary hover:text-primary">Back</button>
              <button onClick={confirmMapping} className="bg-accent text-white px-6 py-2 rounded-md font-medium hover:bg-accent/90">Preview Data</button>
            </div>
          </div>
        )}

        {currentStep === 'preview' && (
          <div className="space-y-6">
            <h3 className="text-lg font-medium text-primary">Dry Run Preview</h3>
            
            <div className="grid grid-cols-3 gap-4 mb-6">
               <div className="bg-background p-4 rounded-lg border border-border">
                  <div className="text-2xl font-bold text-primary">1,204</div>
                  <div className="text-sm text-secondary">Valid Rows</div>
               </div>
               <div className="bg-background p-4 rounded-lg border border-border border-red-500/20">
                  <div className="text-2xl font-bold text-red-500">12</div>
                  <div className="text-sm text-secondary">Errors (Skipped)</div>
               </div>
               <div className="bg-background p-4 rounded-lg border border-border">
                  <div className="text-2xl font-bold text-blue-500">842</div>
                  <div className="text-sm text-secondary">Will Create (362 Update)</div>
               </div>
            </div>

            <div className="flex justify-end gap-3">
              <button onClick={() => setCurrentStep('mapping')} className="px-4 py-2 text-secondary hover:text-primary">Back</button>
              <button onClick={startImport} className="bg-accent text-white px-6 py-2 rounded-md font-medium flex items-center gap-2 hover:bg-accent/90">
                <CheckCircle2 className="w-5 h-5" /> Start Import
              </button>
            </div>
          </div>
        )}

        {currentStep === 'importing' && (
          <div className="py-12 flex flex-col items-center justify-center text-center space-y-6">
            <RefreshCw className="w-12 h-12 text-accent animate-spin" />
            <div>
              <h3 className="text-xl font-bold text-primary mb-2">Importing Data...</h3>
              <p className="text-secondary text-sm">Processing in background chunks to preserve memory.</p>
            </div>
            
            <div className="w-full max-w-md bg-background rounded-full h-3 border border-border overflow-hidden">
              <div 
                className="bg-accent h-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <p className="text-primary font-medium">{progress}% Complete</p>
          </div>
        )}
        
        {currentStep === 'result' && (
          <div className="py-8 flex flex-col items-center justify-center text-center space-y-6">
            <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center text-green-500 mb-2">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-primary mb-2">Import Successful</h3>
              <p className="text-secondary text-sm">Successfully processed 1,204 rows.</p>
            </div>
            
            <div className="flex gap-4">
              <button className="text-red-500 hover:underline text-sm font-medium flex items-center gap-1">
                <AlertCircle className="w-4 h-4" /> Rollback Import
              </button>
              <button onClick={reset} className="bg-accent text-white px-6 py-2 rounded-md font-medium hover:bg-accent/90">
                Import Another
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
