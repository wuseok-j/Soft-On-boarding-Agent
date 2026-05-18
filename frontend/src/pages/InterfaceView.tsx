import React, { useState } from 'react';
import { 
  Folder, FileCode2, CornerDownRight, 
  Palette, Type, Box, Search, Settings2,
  ChevronDown, ChevronRight
} from 'lucide-react';

// Reusable Color Swatch with Copy functionality
const ColorSwatch = ({ name, hex, bgClass }: { name: string, hex: string, bgClass: string }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(hex);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="space-y-2 cursor-pointer group" onClick={handleCopy}>
      <div className={`h-10 w-full ${bgClass} rounded-md border border-gray-200 shadow-sm relative flex items-center justify-center transition-all group-hover:shadow-md`}>
        {copied && <span className="absolute text-[10px] bg-gray-800 text-white px-2 py-0.5 rounded-full font-medium shadow">Copied!</span>}
      </div>
      <div className="text-[10px] font-mono text-gray-500 flex flex-col">
        <span className="text-gray-800 font-semibold">{name}</span> 
        <span>{hex}</span>
      </div>
    </div>
  );
};

export function InterfaceView() {
  const [searchQuery, setSearchQuery] = useState('');
  
  // Folder states
  const [openFolders, setOpenFolders] = useState<Record<string, boolean>>({
    dashboard: true,
    settings: true,
    auth: true,
  });

  const toggleFolder = (folder: string) => {
    setOpenFolders(prev => ({ ...prev, [folder]: !prev[folder] }));
  };

  const componentsData = [
    {
      id: 'button',
      name: 'Button',
      ui: (
        <div className="flex items-center justify-center gap-3 w-full h-full">
          <button className="bg-blue-600 text-white px-4 py-2 rounded-md font-medium text-sm hover:bg-blue-700 transition-colors shadow-sm">
            Primary
          </button>
          <button className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-md font-medium text-sm hover:bg-gray-50 transition-colors shadow-sm">
            Secondary
          </button>
        </div>
      ),
      code: `interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  children: ReactNode;
}`
    },
    {
      id: 'input',
      name: 'Input',
      ui: (
        <div className="w-full max-w-[280px] relative">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-gray-400" />
          <input 
            type="text" 
            placeholder="Search components..." 
            className="w-full bg-white border border-gray-300 rounded-md py-2 pl-9 pr-3 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all shadow-sm" 
            readOnly
          />
        </div>
      ),
      code: `interface InputProps {
  type?: 'text' | 'password' | 'email';
  placeholder?: string;
  icon?: LucideIcon;
  error?: string;
}`
    },
    {
      id: 'badge',
      name: 'Badge',
      ui: (
        <div className="flex items-center justify-center gap-4 w-full h-full">
          <span className="inline-flex items-center rounded-md bg-gray-100 border border-gray-200 px-2 py-1 text-xs font-medium text-gray-600">
            Default
          </span>
          <span className="inline-flex items-center rounded-md bg-blue-50 border border-blue-200 px-2 py-1 text-xs font-medium text-blue-700">
            Active
          </span>
        </div>
      ),
      code: `interface BadgeProps {
  status: 'default' | 'active';
  label: string;
  dot?: boolean;
}`
    },
    {
      id: 'card',
      name: 'Card',
      ui: (
        <div className="bg-white border border-gray-200 rounded-lg p-4 w-full max-w-[240px] shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <Settings2 className="w-4 h-4 text-gray-500" />
            <span className="text-sm font-semibold text-gray-800">Settings</span>
          </div>
          <p className="text-xs text-gray-500">Configure your preferences.</p>
        </div>
      ),
      code: `interface CardProps {
  title: string;
  description?: string;
  icon?: ReactNode;
  children?: ReactNode;
}`
    }
  ];

  const filteredComponents = componentsData.filter(comp => 
    comp.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-full w-full bg-gray-50/50 text-gray-900 p-4 md:p-8 font-sans">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-7xl mx-auto">
        
        {/* 1. Top-Left: Screen-Code Mapping */}
        <div className="col-span-1 bg-white border border-gray-200 rounded-xl shadow-sm flex flex-col">
          <div className="border-b border-gray-100 px-5 py-4 flex items-center justify-between">
            <h3 className="text-sm font-semibold flex items-center gap-2 text-gray-800">
              <Folder className="w-4 h-4 text-blue-500" />
              Screen-Code Mapping
            </h3>
            <span className="text-xs text-gray-500 font-mono tracking-wide bg-gray-100 px-2 py-1 rounded">App Router</span>
          </div>
          <div className="p-5 flex-1 text-sm text-gray-700 font-mono flex flex-col gap-4 overflow-y-auto max-h-[400px]">
            
            <div className="flex items-start gap-2">
              <Folder className="w-4 h-4 text-blue-500 mt-0.5" />
              <div className="text-gray-900 font-medium">src/app</div>
            </div>
            
            <div className="flex flex-col relative before:absolute before:content-[''] before:left-[11px] before:top-0 before:bottom-0 before:w-px before:bg-gray-200 ml-2 pl-6 gap-4">
              
              <div className="flex items-center gap-3 relative">
                <span className="absolute -left-6 top-[11px] w-4 h-px bg-gray-200"></span>
                <FileCode2 className="w-4 h-4 text-gray-400" />
                <span>layout.tsx</span>
                <span className="text-xs bg-gray-100 border border-gray-200 px-2 py-0.5 rounded-full text-gray-500 ml-auto flex items-center gap-1 shadow-sm">
                  <CornerDownRight className="w-3 h-3" /> Root
                </span>
              </div>

              {/* Dashboard Folder */}
              <div className="flex flex-col relative gap-4">
                <div 
                  className="flex items-center gap-2 relative cursor-pointer hover:bg-gray-50 py-1 -ml-1 pl-1 rounded transition-colors"
                  onClick={() => toggleFolder('dashboard')}
                >
                  <span className="absolute -left-5 top-[11px] w-4 h-px bg-gray-200"></span>
                  {openFolders.dashboard ? <ChevronDown className="w-3.5 h-3.5 text-gray-400" /> : <ChevronRight className="w-3.5 h-3.5 text-gray-400" />}
                  <Folder className="w-4 h-4 text-blue-500" />
                  <span className="font-medium">(dashboard)</span>
                </div>
                
                {openFolders.dashboard && (
                  <div className="flex flex-col relative before:absolute before:content-[''] before:left-[15px] before:top-0 before:bottom-4 before:w-px before:bg-gray-200 ml-2 pl-7 gap-4">
                    <div className="flex items-center gap-3 relative">
                      <span className="absolute -left-7 top-[11px] w-5 h-px bg-gray-200"></span>
                      <FileCode2 className="w-4 h-4 text-green-500" />
                      <span>page.tsx</span>
                      <span className="text-xs bg-green-50 border border-green-200 text-green-700 px-2 py-0.5 rounded-full ml-auto flex items-center gap-1 shadow-sm">
                        <CornerDownRight className="w-3 h-3" /> /dashboard
                      </span>
                    </div>
                    
                    <div className="flex flex-col gap-4 relative">
                      <div 
                        className="flex items-center gap-2 relative cursor-pointer hover:bg-gray-50 py-1 -ml-1 pl-1 rounded transition-colors"
                        onClick={() => toggleFolder('settings')}
                      >
                        <span className="absolute -left-6 top-[11px] w-4 h-px bg-gray-200"></span>
                        {openFolders.settings ? <ChevronDown className="w-3.5 h-3.5 text-gray-400" /> : <ChevronRight className="w-3.5 h-3.5 text-gray-400" />}
                        <Folder className="w-4 h-4 text-blue-500" />
                        <span className="font-medium">settings</span>
                      </div>
                      
                      {openFolders.settings && (
                        <div className="flex flex-col relative ml-3 pl-6 gap-4">
                          <div className="flex items-center gap-3 relative">
                            <span className="absolute -left-[23px] -top-[16px] w-px h-7 bg-gray-200"></span>
                            <span className="absolute -left-[23px] top-[11px] w-4 h-px bg-gray-200"></span>
                            <FileCode2 className="w-4 h-4 text-green-500" />
                            <span>page.tsx</span>
                            <span className="text-xs bg-green-50 border border-green-200 text-green-700 px-2 py-0.5 rounded-full ml-auto flex items-center gap-1 shadow-sm">
                              <CornerDownRight className="w-3 h-3" /> /dashboard/settings
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Auth Folder */}
              <div className="flex flex-col relative gap-4">
                <div 
                  className="flex items-center gap-2 relative cursor-pointer hover:bg-gray-50 py-1 -ml-1 pl-1 rounded transition-colors"
                  onClick={() => toggleFolder('auth')}
                >
                  <span className="absolute -left-5 top-[11px] w-4 h-px bg-gray-200"></span>
                  {openFolders.auth ? <ChevronDown className="w-3.5 h-3.5 text-gray-400" /> : <ChevronRight className="w-3.5 h-3.5 text-gray-400" />}
                  <Folder className="w-4 h-4 text-blue-500" />
                  <span className="font-medium">auth</span>
                </div>
                
                {openFolders.auth && (
                  <div className="flex flex-col relative ml-3 pl-6 gap-4">
                    <div className="flex items-center gap-3 relative">
                      <span className="absolute -left-[23px] -top-[16px] w-px h-7 bg-gray-200"></span>
                      <span className="absolute -left-[23px] top-[11px] w-4 h-px bg-gray-200"></span>
                      <FileCode2 className="w-4 h-4 text-indigo-500" />
                      <span>login/page.tsx</span>
                      <span className="text-xs bg-indigo-50 border border-indigo-200 text-indigo-700 px-2 py-0.5 rounded-full ml-auto flex items-center gap-1 shadow-sm">
                        <CornerDownRight className="w-3 h-3" /> /auth/login
                      </span>
                    </div>
                  </div>
                )}
              </div>

            </div>
          </div>
        </div>

        {/* 2. Top-Right: Design System Tokens */}
        <div className="col-span-1 bg-white border border-gray-200 rounded-xl shadow-sm flex flex-col">
          <div className="border-b border-gray-100 px-5 py-4 flex items-center justify-between">
            <h3 className="text-sm font-semibold flex items-center gap-2 text-gray-800">
              <Palette className="w-4 h-4 text-blue-500" />
              Design Tokens
            </h3>
            <span className="text-xs text-gray-500 font-mono tracking-wide bg-gray-100 px-2 py-1 rounded">tailwind.config (Click to Copy)</span>
          </div>
          
          <div className="p-5 flex flex-col gap-8 flex-1">
            <div>
              <h4 className="text-[11px] text-gray-400 font-bold uppercase tracking-widest mb-4 flex items-center gap-2">
                Color Palette
              </h4>
              <div className="grid grid-cols-4 gap-4">
                <ColorSwatch name="Primary" hex="#3B82F6" bgClass="bg-blue-500" />
                <ColorSwatch name="Surface" hex="#FFFFFF" bgClass="bg-white" />
                <ColorSwatch name="Border" hex="#E5E7EB" bgClass="bg-gray-200" />
                <ColorSwatch name="Muted" hex="#9CA3AF" bgClass="bg-gray-400" />
              </div>
            </div>

            <div>
              <h4 className="text-[11px] text-gray-400 font-bold uppercase tracking-widest mb-4 flex items-center gap-2">
                Typography
              </h4>
              <div className="border border-gray-200 rounded-lg overflow-hidden shadow-sm">
                <table className="w-full text-left text-xs">
                  <thead className="bg-gray-50 border-b border-gray-200 text-gray-600">
                    <tr>
                      <th className="px-4 py-3 font-semibold">Scale</th>
                      <th className="px-4 py-3 font-semibold">Size</th>
                      <th className="px-4 py-3 font-semibold">Weight</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 text-gray-700 bg-white">
                    <tr className="hover:bg-gray-50/50 transition-colors">
                      <td className="px-4 py-3 font-bold text-gray-900">H1</td>
                      <td className="px-4 py-3 font-mono text-[10px]">2.25rem</td>
                      <td className="px-4 py-3">600 (Semibold)</td>
                    </tr>
                    <tr className="hover:bg-gray-50/50 transition-colors">
                      <td className="px-4 py-3 font-semibold text-gray-900">H2</td>
                      <td className="px-4 py-3 font-mono text-[10px]">1.5rem</td>
                      <td className="px-4 py-3">500 (Medium)</td>
                    </tr>
                    <tr className="hover:bg-gray-50/50 transition-colors">
                      <td className="px-4 py-3 text-gray-700">Body</td>
                      <td className="px-4 py-3 font-mono text-[10px]">0.875rem</td>
                      <td className="px-4 py-3">400 (Regular)</td>
                    </tr>
                    <tr className="hover:bg-gray-50/50 transition-colors">
                      <td className="px-4 py-3 text-gray-500">Caption</td>
                      <td className="px-4 py-3 font-mono text-[10px]">0.75rem</td>
                      <td className="px-4 py-3">400 (Regular)</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        {/* 3. Bottom: Component Blueprint Catalog */}
        <div className="col-span-1 lg:col-span-2 bg-white border border-gray-200 rounded-xl shadow-sm flex flex-col">
          <div className="border-b border-gray-100 px-5 py-4 flex items-center justify-between bg-white rounded-t-xl">
            <h3 className="text-sm font-semibold flex items-center gap-2 text-gray-800">
              <Box className="w-4 h-4 text-blue-500" />
              Component Blueprint Catalog
            </h3>
            
            <div className="flex items-center gap-3">
              <div className="relative">
                <Search className="w-3.5 h-3.5 absolute left-2.5 top-2 text-gray-400" />
                <input 
                  type="text" 
                  placeholder="Search components..." 
                  className="pl-8 pr-3 py-1.5 text-xs bg-gray-50 border border-gray-200 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 w-48 transition-all"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <span className="text-xs text-gray-500 font-mono tracking-wide bg-gray-100 px-2 py-1 rounded">
                {filteredComponents.length} Components
              </span>
            </div>
          </div>
          
          <div className="flex flex-col divide-y divide-gray-100">
            {filteredComponents.length > 0 ? (
              filteredComponents.map((comp) => (
                <div key={comp.id} className="flex flex-col md:flex-row hover:bg-gray-50/30 transition-colors">
                  <div className="w-full md:w-1/2 p-6 border-b md:border-b-0 md:border-r border-gray-100 flex items-center justify-center min-h-[160px] bg-gray-50/50">
                    {comp.ui}
                  </div>
                  <div className="w-full md:w-1/2 p-6 bg-[#0d1117] text-[11px] font-mono text-gray-300 overflow-x-auto min-h-[160px] flex items-center relative group">
                    <button 
                      className="absolute top-3 right-3 text-gray-500 hover:text-white bg-white/5 hover:bg-white/10 px-2 py-1 rounded text-[10px] opacity-0 group-hover:opacity-100 transition-all"
                      onClick={() => navigator.clipboard.writeText(comp.code)}
                    >
                      Copy code
                    </button>
                    <pre className="leading-relaxed"><code>
                      {/* Very basic syntax highlighting for TS Interface via inline classes */}
                      <span className="text-[#ff7b72]">interface</span> <span className="text-[#d2a8ff]">{comp.name}Props</span> {'{\n'}
                      {comp.code.split('\n').slice(1, -1).map((line, i) => (
                        <div key={i}>
                          <span className="text-[#79c0ff]">{line.split(':')[0]}</span>:
                          <span className="text-[#a5d6ff]">{line.split(':')[1]}</span>
                        </div>
                      ))}
                      {'}'}
                    </code></pre>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-10 text-center text-gray-500 text-sm flex flex-col items-center">
                <Search className="w-8 h-8 text-gray-300 mb-2" />
                No components found matching "{searchQuery}"
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

