import React, { useEffect, useMemo, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import MarkerClusterGroup from 'react-leaflet-cluster';
import 'leaflet/dist/leaflet.css';
import 'react-leaflet-cluster/dist/assets/MarkerCluster.css';
import 'react-leaflet-cluster/dist/assets/MarkerCluster.Default.css';
import { TaskLocation, getCategoryColor } from '../../data/seedTasks';

// Fix for default markers
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl:
    'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl:
    'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

interface LeafletMapProps {
  tasks: TaskLocation[];
  onTaskSelect?: (task: TaskLocation) => void;
  height?: string;
  enableClustering?: boolean;
}

const CITYU_CENTER: [number, number] = [22.3364, 114.2734];

// Custom marker icon
const createCustomIcon = (task: TaskLocation): L.DivIcon => {
  const color = getCategoryColor(task.category);
  const difficultyStars =
    task.difficulty === 'easy' ? '⭐' : task.difficulty === 'medium' ? '⭐⭐' : '⭐⭐⭐';
  const statusIcon =
    task.status === 'available' ? '🎯' : task.status === 'in_progress' ? '⏳' : '✅';

  // This uses inline styles but with CSS variables for theming
  return L.divIcon({
    html: `
      <div style="
        background-color: ${color};
        width: 32px;
        height: 32px;
        border-radius: 50%;
        border: 2px solid rgb(var(--color-bg-secondary));
        display: flex; align-items: center; justify-content: center;
        font-size: 12px; color: white; font-weight: bold;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3); position: relative;
      ">
        ${difficultyStars.charAt(0)}
        <div style="
          position: absolute; top: -8px; right: -8px;
          font-size: 10px; background: rgb(var(--color-bg-secondary)); color: rgb(var(--color-text-primary));
          border-radius: 50%; width: 16px; height: 16px;
          display: flex; align-items: center; justify-content: center;
          box-shadow: 0 1px 2px rgba(0,0,0,0.2);
          border: 1px solid rgb(var(--color-border));
        ">
          ${statusIcon}
        </div>
      </div>
    `,
    className: 'custom-marker', // Keep class for potential future styling
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16],
  });
};

// Safe bounds handler
const MapBoundsHandler: React.FC<{ tasks: TaskLocation[] }> = ({ tasks }) => {
  const map = useMap();

  useEffect(() => {
    if (!map) return;
    if (!tasks || tasks.length === 0) return;

    try {
      const bounds = L.latLngBounds(
        tasks.map((t) => [t.location.lat, t.location.lng] as [number, number])
      );
      if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [20, 20], maxZoom: 18 });
      }
    } catch (e) {
      // eslint-disable-next-line no-console
      console.warn('Map fitBounds skipped:', e);
    }
  }, [map, tasks]);

  return null;
};

const LeafletMap: React.FC<LeafletMapProps> = ({
  tasks,
  onTaskSelect,
  height = '500px',
  enableClustering = false,
}) => {
  const mapRef = useRef<L.Map | null>(null);

  const markers = useMemo(
    () =>
      tasks.map((task) => ({
        task,
        position: [task.location.lat, task.location.lng] as [number, number],
        icon: createCustomIcon(task),
      })),
    [tasks]
  );

  const handleMarkerClick = (task: TaskLocation) => {
    onTaskSelect?.(task);
  };

  return (
    <div
      style={{ height, width: '100%', zIndex: 'var(--z-map)' }}
      className="relative rounded-lg overflow-hidden border border-border"
    >
      <MapContainer
        center={CITYU_CENTER}
        zoom={16}
        style={{ height: '100%', width: '100%' }}
        ref={mapRef as any}
        zoomControl
        scrollWheelZoom
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <MapBoundsHandler tasks={tasks} />

        {enableClustering ? (
          <MarkerClusterGroup>
            {markers.map(({ task, position, icon }) => (
              <Marker
                key={task.task_id}
                position={position}
                icon={icon}
                eventHandlers={{ click: () => handleMarkerClick(task) }}
              >
                <Popup>
                  <div className="w-64 text-text-primary">
                    <h3 className="m-0 mb-2 text-sm font-bold text-primary">
                      {task.title}
                    </h3>
                    <p className="m-0 mb-2 text-xs text-text-secondary">
                      {task.description}
                    </p>
                    <div className="flex flex-wrap gap-1.5 mb-2">
                      <span
                        className="text-white px-1.5 py-0.5 rounded-md text-xs"
                        style={{ backgroundColor: getCategoryColor(task.category) }}
                      >
                        {task.category}
                      </span>
                      <span className="bg-bg-tertiary text-text-secondary px-1.5 py-0.5 rounded-md text-xs border border-border">
                        {task.difficulty === 'easy' && '⭐ 简单'}
                        {task.difficulty === 'medium' && '⭐⭐ 中等'}
                        {task.difficulty === 'hard' && '⭐⭐⭐ 困难'}
                      </span>
                      <span className="bg-bg-tertiary text-text-secondary px-1.5 py-0.5 rounded-md text-xs border border-border">
                        {task.status === 'available' && '🎯 可接取'}
                        {task.status === 'in_progress' && '⏳ 进行中'}
                        {task.status === 'completed' && '✅ 已完成'}
                      </span>
                    </div>
                    <div className="text-xs text-text-muted space-y-1">
                      <div>📍 {task.location.name}</div>
                      {task.estimatedTime && <div>⏱️ {task.estimatedTime} 分钟</div>}
                      {task.course && <div>📚 {task.course}</div>}
                    </div>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MarkerClusterGroup>
        ) : (
          markers.map(({ task, position, icon }) => (
            <Marker
              key={task.task_id}
              position={position}
              icon={icon}
              eventHandlers={{ click: () => handleMarkerClick(task) }}
            >
              <Popup>
                <div className="w-64 text-text-primary">
                  <h3 className="m-0 mb-2 text-sm font-bold text-primary">
                    {task.title}
                  </h3>
                  <p className="m-0 mb-2 text-xs text-text-secondary">
                    {task.description}
                  </p>
                  <div className="flex flex-wrap gap-1.5 mb-2">
                    <span
                      className="text-white px-1.5 py-0.5 rounded-md text-xs"
                      style={{ backgroundColor: getCategoryColor(task.category) }}
                    >
                      {task.category}
                    </span>
                    <span className="bg-bg-tertiary text-text-secondary px-1.5 py-0.5 rounded-md text-xs border border-border">
                      {task.difficulty === 'easy' && '⭐ 简单'}
                      {task.difficulty === 'medium' && '⭐⭐ 中等'}
                      {task.difficulty === 'hard' && '⭐⭐⭐ 困难'}
                    </span>
                    <span className="bg-bg-tertiary text-text-secondary px-1.5 py-0.5 rounded-md text-xs border border-border">
                      {task.status === 'available' && '🎯 可接取'}
                      {task.status === 'in_progress' && '⏳ 进行中'}
                      {task.status === 'completed' && '✅ 已完成'}
                    </span>
                  </div>
                  <div className="text-xs text-text-muted space-y-1">
                    <div>📍 {task.location.name}</div>
                    {task.estimatedTime && <div>⏱️ {task.estimatedTime} 分钟</div>}
                    {task.course && <div>📚 {task.course}</div>}
                  </div>
                </div>
              </Popup>
            </Marker>
          ))
        )}
      </MapContainer>
    </div>
  );
};

export default LeafletMap;