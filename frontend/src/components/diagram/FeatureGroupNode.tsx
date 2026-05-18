import { memo } from 'react';
import { type NodeProps, NodeResizer } from 'reactflow';

export const FeatureGroupNode = memo(({ data, selected }: NodeProps) => {
  return (
    <>
      <NodeResizer color="#cbd5e1" isVisible={selected} minWidth={300} minHeight={200} />
      <div className="w-full h-full bg-gray-50/50 border-2 border-dashed border-gray-300 rounded-xl relative pointer-events-none">
        <div className="absolute -top-3 left-4 bg-white px-2 py-0.5 rounded-full border border-gray-200 shadow-sm flex items-center">
          <span className="text-xs font-semibold text-gray-600 tracking-wide">{data.label}</span>
        </div>
      </div>
    </>
  );
});

FeatureGroupNode.displayName = 'FeatureGroupNode';
