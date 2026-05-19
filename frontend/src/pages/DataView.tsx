import { useMemo, useState, useEffect } from 'react';
import axios from 'axios';
import ReactFlow, {
  Background,
  Controls,
  EdgeLabelRenderer,
  BaseEdge,
  getSmoothStepPath,
  Handle,
  Position,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { User, ShoppingCart, FileText, Database, Table as TableIcon } from 'lucide-react';

const iconMap: Record<string, any> = {
  User: User,
  ShoppingCart: ShoppingCart,
  FileText: FileText,
  Database: Database,
  Table: TableIcon
};

const TableNode = ({ data }: any) => {
  const Icon = (typeof data.icon === 'string' ? iconMap[data.icon] : data.icon) || TableIcon;
  return (
    <div className="w-72 bg-white rounded-xl shadow-[0_4px_20px_rgba(0,0,0,0.04)] border border-gray-200">
      <Handle type="target" position={Position.Top} id="top" className="opacity-0" />
      <Handle type="source" position={Position.Bottom} id="bottom" className="opacity-0" />
      <Handle type="target" position={Position.Left} id="left" className="opacity-0" />
      <Handle type="source" position={Position.Right} id="right" className="opacity-0" />

      <div className="flex items-center gap-3 p-4 border-b border-gray-100">
        <div className="w-8 h-8 rounded-full bg-gray-50 flex items-center justify-center flex-shrink-0">
          <Icon className="w-4 h-4 text-gray-700" />
        </div>
        <span className="text-base font-semibold text-gray-900">{data.title}</span>
      </div>
      <div className="p-4 flex flex-col gap-3">
        {data.columns.map((col: any, idx: number) => (
          <div key={idx} className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">{col.name}</span>
              {col.badge && (
                <span className="px-1.5 py-0.5 rounded bg-gray-100 text-gray-600 text-[10px] font-bold tracking-wider">
                  {col.badge}
                </span>
              )}
            </div>
            <span className="text-xs text-gray-500 font-mono">{col.type}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

const CustomEdge = ({
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
  markerEnd,
  data,
}: any) => {
  const [edgePath, labelX, labelY] = getSmoothStepPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
    borderRadius: 0,
  });

  return (
    <>
      <BaseEdge path={edgePath} markerEnd={markerEnd} style={{ ...style, strokeWidth: 2, stroke: '#E5E7EB' }} />
      {data?.label && (
        <EdgeLabelRenderer>
          <div
            style={{
              position: 'absolute',
              transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,
              pointerEvents: 'all',
            }}
            className={data.labelClassName}
          >
            {data.label}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
};



export function DataView() {
  const nodeTypes = useMemo(() => ({ tableNode: TableNode }), []);
  const edgeTypes = useMemo(() => ({ customEdge: CustomEdge }), []);

  const [nodes, setNodes] = useState<any[]>([]);
  const [edges, setEdges] = useState<any[]>([]);
  const [tasks, setTasks] = useState<string[]>([]);
  const [criticalFiles, setCriticalFiles] = useState<string[]>([]);
  const [schemaPreview, setSchemaPreview] = useState<string>('');

  useEffect(() => {
    const fetchSchemaData = async () => {
      try {
        // 하드코딩된 임시 리포지토리 URL (추후 동적으로 변경 가능)
        const repositoryUrl = "vector/onboarding"; 
        const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';
        
        const response = await axios.get(`${API_BASE}/api/v1/data-view/schema?repositoryUrl=${repositoryUrl}`);
        
        if (response.data) {
          if (response.data.nodes && response.data.nodes.length > 0) {
            setNodes(response.data.nodes);
          }
          if (response.data.edges) {
            setEdges(response.data.edges);
          }
          if (response.data.tasks) {
            setTasks(response.data.tasks);
          }
          if (response.data.criticalFiles) {
            setCriticalFiles(response.data.criticalFiles);
          }
          if (response.data.schemaPreview) {
            setSchemaPreview(response.data.schemaPreview);
          }
        }
      } catch (error) {
        console.error("백엔드 API 호출 실패, 기본 더미 데이터를 유지합니다.", error);
      }
    };

    fetchSchemaData();
  }, []);

  return (
    <div className="w-full h-full relative overflow-hidden flex">
      {/* Main Diagram Area with React Flow */}
      <div className="flex-1 relative w-full h-full">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          fitView
          fitViewOptions={{ padding: 0.5, includeHiddenNodes: true }}
          minZoom={0.5}
          maxZoom={2}
          className="bg-dot-pattern"
          nodesDraggable={false} // Adjust as needed
          panOnDrag={true}
          zoomOnScroll={true}
        >
          <Background color="#E5E7EB" gap={16} size={1} />
          <Controls className="mb-4 ml-4" />
        </ReactFlow>
      </div>

      {/* Right Sidebar - Data Analysis & Tasks */}
      <div className="absolute top-8 right-8 w-80 bg-white rounded-2xl shadow-[0_8px_30px_rgba(0,0,0,0.04)] border border-gray-100 p-6 z-20 flex flex-col max-h-[calc(100vh-64px)] overflow-y-auto">
        <h2 className="text-xl font-bold text-gray-900 mb-2 leading-tight">Data Analysis &<br />Tasks</h2>
        <p className="text-sm text-gray-500 mb-8">Pending schema optimizations.</p>

        {/* To-Do Items */}
        <div className="mb-8">
          <h3 className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-4">To-Do Items</h3>
          <ul className="space-y-4">
            {tasks.map((task, idx) => (
              <li key={idx} className="flex items-start gap-3">
                <div className="mt-0.5 w-4 h-4 rounded border border-gray-300 flex-shrink-0 bg-white"></div>
                <span className="text-sm text-gray-700 leading-snug">{task}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Critical Schema Files */}
        <div className="mb-8">
          <h3 className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-4">Critical Schema Files</h3>
          <div className="space-y-2">
            {criticalFiles.map((file, idx) => (
              <div key={idx} className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors">
                <FileText className="w-4 h-4 text-gray-500" />
                <span className="text-xs font-mono text-gray-700">{file}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Schema Preview */}
        <div>
          <h3 className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-4">Schema Preview</h3>
          <div className="bg-[#2D2D2D] rounded-xl p-4 overflow-x-auto shadow-inner">
            <pre className="text-[11px] font-mono leading-relaxed text-gray-300">
              {schemaPreview || 'No preview available'}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
