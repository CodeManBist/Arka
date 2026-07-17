"use client";

import { useEffect, useRef, useState, useCallback } from 'react';
import * as d3 from 'd3';

type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

type GraphNode = {
  id: string;
  name: string;
  type: string;
  file_path: string;
  risk_level?: RiskLevel;
  is_changed?: boolean;
  depth?: number;
};

type GraphEdge = {
  source: string;
  target: string;
  type: string;
};

type GraphData = {
  nodes: GraphNode[];
  edges: GraphEdge[];
};

const RISK_COLORS: Record<RiskLevel, string> = {
  critical: '#ef4444',
  high: '#f97316',
  medium: '#eab308',
  low: '#22c55e',
};

const DEFAULT_COLOR = '#6b7280';
const CHANGED_COLOR = '#3b82f6';

interface GraphVisualizationProps {
  data: GraphData;
  changedSymbol?: string;
  loading?: boolean;
  className?: string;
}

export default function GraphVisualization({
  data,
  changedSymbol,
  loading = false,
  className = ''
}: GraphVisualizationProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [isAnimating, setIsAnimating] = useState(false);

  // Update dimensions on resize
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        setDimensions({
          width: Math.max(rect.width, 400),
          height: Math.max(rect.height, 400)
        });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    
    return () => {
      window.removeEventListener('resize', updateDimensions);
    };
  }, []);

  // Create the graph
  useEffect(() => {
    if (!data || !svgRef.current || loading) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove(); // Clear previous graph

    const { nodes, edges } = data;
    
    if (nodes.length === 0) {
      // Show empty state
      svg.append('text')
        .attr('x', dimensions.width / 2)
        .attr('y', dimensions.height / 2)
        .attr('text-anchor', 'middle')
        .attr('class', 'text-gray-400 dark:text-gray-500')
        .text('No graph data available');
      return;
    }

    // Create a force simulation
    const simulation = d3.forceSimulation<GraphNode>(nodes)
      .force('link', d3.forceLink<GraphNode, GraphEdge>(edges).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody<GraphNode>().strength(-200))
      .force('center', d3.forceCenter(dimensions.width / 2, dimensions.height / 2))
      .force('collision', d3.forceCollide<GraphNode>().radius(30));

    // Create links
    const link = svg.append('g')
      .selectAll('line')
      .data(edges)
      .join('line')
      .attr('stroke', '#9ca3af')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', 1.5);

    // Create node groups
    const node = svg.append('g')
      .selectAll('g')
      .data(nodes)
      .join('g')
      .call(
        d3.drag<SVGGElement, GraphNode>()
          .on('start', dragstarted)
          .on('drag', dragged)
          .on('end', dragended)
      )
      .on('click', (event, d) => {
        event.stopPropagation();
        setSelectedNode(d);
        
        // Highlight connections
        link
          .attr('stroke', (e: GraphEdge) => 
            e.source === d.id || e.target === d.id ? '#3b82f6' : '#9ca3af'
          )
          .attr('stroke-width', (e: GraphEdge) => 
            e.source === d.id || e.target === d.id ? 2.5 : 1.5
          );
      });

    // Add circles for nodes
    node.append('circle')
      .attr('r', (d: GraphNode) => {
        if (d.is_changed) return 12;
        if (d.depth === 1) return 10;
        if (d.depth === 2) return 8;
        return 6;
      })
      .attr('fill', (d: GraphNode) => {
        if (d.is_changed) return CHANGED_COLOR;
        if (d.risk_level) return RISK_COLORS[d.risk_level];
        return DEFAULT_COLOR;
      })
      .attr('stroke', (d: GraphNode) => {
        if (d.is_changed) return '#fff';
        return d3.color(RISK_COLORS[d.risk_level || 'low'])?.darker(0.5)?.toString() || '#fff';
      })
      .attr('stroke-width', 2)
      .attr('class', 'cursor-pointer hover:opacity-80 transition-all duration-200')
      .transition()
        .duration(500)
        .attr('r', (d: GraphNode) => {
          if (d.is_changed) return 12;
          if (d.depth === 1) return 10;
          if (d.depth === 2) return 8;
          return 6;
        });

    // Add labels
    node.append('text')
      .text((d: GraphNode) => {
        // Shorten long names
        const maxLength = 12;
        if (d.name.length > maxLength) {
          return d.name.substring(0, maxLength - 2) + '..';
        }
        return d.name;
      })
      .attr('x', 15)
      .attr('y', 4)
      .attr('class', 'text-sm font-medium text-gray-700 dark:text-gray-300')
      .attr('pointer-events', 'none');

    // Add risk level indicators for changed nodes
    node.filter((d: GraphNode) => d.is_changed)
      .append('text')
      .text('💥')
      .attr('x', -15)
      .attr('y', 4)
      .attr('class', 'text-lg')
      .attr('pointer-events', 'none');

    // Add pulsing animation for changed node
    node.filter((d: GraphNode) => d.is_changed)
      .select('circle')
      .attr('class', 'cursor-pointer hover:opacity-80 transition-all duration-200 animate-pulse');

    // Update positions on each tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node
        .attr('transform', (d: any) => `translate(${d.x},${d.y})`);
    });

    // Handle drag events
    function dragstarted(event: any, d: GraphNode) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event: any, d: GraphNode) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event: any, d: GraphNode) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    // Add zoom and pan
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        svg.select('g').attr('transform', event.transform);
      });

    svg.call(zoom);

    // Center the graph
    setTimeout(() => {
      const centerX = dimensions.width / 2;
      const centerY = dimensions.height / 2;
      svg.transition()
        .duration(750)
        .call(zoom.transform, d3.zoomIdentity.translate(centerX, centerY).scale(0.8));
    }, 100);

    // Cleanup on unmount
    return () => {
      simulation.stop();
    };
  }, [data, dimensions, loading, changedSymbol]);

  // Start blast radius animation
  const startBlastAnimation = useCallback(() => {
    if (!data || !svgRef.current) return;

    setIsAnimating(true);
    
    const svg = d3.select(svgRef.current);
    const nodes = svg.selectAll('circle');
    
    // Find changed node
    const changedNode = data.nodes.find(n => n.is_changed);
    if (!changedNode) return;

    // Animate nodes outward in waves based on depth
    nodes
      .filter((d: any) => d.depth !== undefined)
      .transition()
      .duration(1000)
      .delay((d: any, i: number) => i * 100)
      .attr('r', (d: any) => {
        if (d.is_changed) return 15;
        if (d.depth === 1) return 12;
        if (d.depth === 2) return 10;
        return 8;
      })
      .transition()
      .duration(500)
      .attr('r', (d: any) => {
        if (d.is_changed) return 12;
        if (d.depth === 1) return 10;
        if (d.depth === 2) return 8;
        return 6;
      });

    setTimeout(() => setIsAnimating(false), 2000);
  }, [data]);

  // Reset view
  const resetView = useCallback(() => {
    if (!svgRef.current) return;
    
    const svg = d3.select(svgRef.current);
    const zoom = d3.zoom<SVGSVGElement, unknown>();
    
    svg.transition()
      .duration(750)
      .call(zoom.transform, d3.zoomIdentity);
  }, []);

  if (loading) {
    return (
      <div 
        ref={containerRef} 
        className={`bg-gray-50 dark:bg-gray-900 rounded-xl p-8 min-h-96 flex items-center justify-center ${className}`}
      >
        <div className="text-center">
          <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/30 rounded-full mx-auto mb-4 flex items-center justify-center">
            <svg className="w-8 h-8 text-blue-600 dark:text-blue-400 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          </div>
          <p className="text-gray-500 dark:text-gray-400">Loading graph...</p>
        </div>
      </div>
    );
  }

  if (!data || data.nodes.length === 0) {
    return (
      <div 
        ref={containerRef} 
        className={`bg-gray-50 dark:bg-gray-900 rounded-xl p-8 min-h-96 flex flex-col items-center justify-center ${className}`}
      >
        <div className="w-24 h-24 bg-gray-100 dark:bg-gray-700 rounded-full mx-auto mb-4 flex items-center justify-center">
          <svg className="w-12 h-12 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <p className="text-gray-500 dark:text-gray-400 mb-2">
          Run an analysis first to visualize the blast radius
        </p>
        <p className="text-sm text-gray-400 dark:text-gray-500">
          The interactive graph will show nodes pulsing outward from changed symbols,
          color-coded by risk level.
        </p>
      </div>
    );
  }

  return (
    <div className={`rounded-xl overflow-hidden ${className}`}>
      {/* Controls */}
      <div className="bg-white dark:bg-gray-800 p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Blast Radius Graph
          </h3>
          {changedSymbol && (
            <span className="bg-blue-100 dark:bg-blue-900/30 px-3 py-1 rounded-full text-sm text-blue-700 dark:text-blue-300">
              Changed: {changedSymbol}
            </span>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={startBlastAnimation}
            disabled={isAnimating}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-lg text-sm font-medium transition-colors flex items-center space-x-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h5M20 20v-5h-5M4 20h5v-5M20 4h-5v5" />
            </svg>
            <span>Animate Blast Radius</span>
          </button>
          <button
            onClick={resetView}
            className="px-4 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h5M20 20v-5h-5M4 20h5v-5M20 4h-5v5" />
            </svg>
            <span>Reset View</span>
          </button>
        </div>
      </div>
      
      {/* Graph Container */}
      <div 
        ref={containerRef} 
        className="bg-gray-50 dark:bg-gray-900 min-h-96 relative"
      >
        <svg 
          ref={svgRef} 
          className="w-full h-full" 
          preserveAspectRatio="xMidYMid meet"
        />
        
        {/* Node Details Tooltip */}
        {selectedNode && (
          <div className="absolute top-4 right-4 bg-white dark:bg-gray-800 rounded-xl p-4 shadow-2xl border border-gray-200 dark:border-gray-700 max-w-xs z-50">
            <button
              onClick={() => setSelectedNode(null)}
              className="absolute top-2 right-2 text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-400"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            
            <div className="pr-6">
              <h4 className="font-bold text-gray-900 dark:text-gray-100 mb-2">{selectedNode.name}</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Type</span>
                  <span className="font-medium text-gray-900 dark:text-gray-100">{selectedNode.type}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">File</span>
                  <span className="font-medium text-gray-900 dark:text-gray-100 truncate">{selectedNode.file_path}</span>
                </div>
                {selectedNode.risk_level && (
                  <div className="flex justify-between items-center">
                    <span className="text-gray-500 dark:text-gray-400">Risk</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${RISK_BADGE_COLORS[selectedNode.risk_level]} text-white`}>
                      {selectedNode.risk_level.toUpperCase()}
                    </span>
                  </div>
                )}
                {selectedNode.is_changed && (
                  <div className="text-center pt-2 border-t border-gray-200 dark:border-gray-700">
                    <span className="text-blue-600 dark:text-blue-400 font-medium">💥 Changed Symbol</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Legend */}
      <div className="bg-white dark:bg-gray-800 p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-center space-x-6">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-blue-600" />
            <span className="text-sm text-gray-600 dark:text-gray-400">Changed Symbol</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-red-600" />
            <span className="text-sm text-gray-600 dark:text-gray-400">Critical</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-orange-600" />
            <span className="text-sm text-gray-600 dark:text-gray-400">High</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-yellow-500" />
            <span className="text-sm text-gray-600 dark:text-gray-400">Medium</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-green-600" />
            <span className="text-sm text-gray-600 dark:text-gray-400">Low</span>
          </div>
        </div>
        <p className="text-xs text-gray-400 dark:text-gray-500 text-center mt-2">
          Click on nodes to see details. Drag to move nodes. Scroll to zoom.
        </p>
      </div>
    </div>
  );
}
