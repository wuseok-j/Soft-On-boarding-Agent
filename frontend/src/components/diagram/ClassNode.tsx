import { memo } from 'react';
import { Handle, Position, type NodeProps } from 'reactflow';
import { Sparkles, Code2, Server, Database, Cloud } from 'lucide-react';

const layerConfig: Record<string, { color: string; icon: any; bg: string }> = {
  Controller: { color: 'border-blue-500', icon: Code2, bg: 'bg-blue-50 text-blue-600' },
  Service: { color: 'border-purple-500', icon: Server, bg: 'bg-purple-50 text-purple-600' },
  Repository: { color: 'border-green-500', icon: Database, bg: 'bg-green-50 text-green-600' },
  External: { color: 'border-orange-500', icon: Cloud, bg: 'bg-orange-50 text-orange-600' },
};

export const ClassNode = memo(({ data, isConnectable }: NodeProps) => {
  const config = layerConfig[data.layer] || { color: 'border-gray-500', icon: Code2, bg: 'bg-gray-50 text-gray-600' };
  const Icon = config.icon;

  return (
    <div className={`
      relative min-w-[200px] bg-white rounded-lg shadow-sm border border-gray-200 
      border-l-4 ${config.color} 
      transition-all duration-300 hover:shadow-md
      ${data.isLastWorked ? 'shadow-[0_0_15px_rgba(168,85,247,0.4)] animate-pulse border-purple-400' : ''}
    `}>
      
      {/* Handles for edges */}
      <Handle type="target" position={Position.Left} isConnectable={isConnectable} className="w-2 h-2 !bg-gray-400" />
      <Handle type="source" position={Position.Right} isConnectable={isConnectable} className="w-2 h-2 !bg-gray-400" />

      {/* Last worked badge */}
      {data.isLastWorked && (
        <div className="absolute -top-3 -right-3 bg-purple-100 border border-purple-200 text-purple-700 text-[10px] font-bold px-2 py-1 rounded-full flex items-center gap-1 shadow-sm z-10 animate-none">
          <Sparkles className="w-3 h-3" />
          <span>마지막 작업</span>
        </div>
      )}

      <div className="p-4 flex items-start gap-3">
        <div className={`p-2 rounded-md ${config.bg}`}>
          <Icon className="w-5 h-5" />
        </div>
        <div>
          <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">{data.layer}</div>
          <div className="text-sm font-bold text-gray-800">{data.name}</div>
        </div>
      </div>
    </div>
  );
});

ClassNode.displayName = 'ClassNode';
