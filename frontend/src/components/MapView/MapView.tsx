import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { ScenarioType, Site, Target } from '../../App';
import { getDeploymentSites, getScenarioTargets } from '../../services/api';
import './MapView.css';

// Fix for default Leaflet icons
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// --- Custom Icons with more reliable URLs ---
const siteIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="blue" stroke="white" stroke-width="2"/></svg>',
  iconSize: [20, 20],
  iconAnchor: [10, 10],
  popupAnchor: [0, -10]
});

const qatarInactiveIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="gray" stroke="white" stroke-width="2"/></svg>',
  iconSize: [20, 20],
  iconAnchor: [10, 10],
  popupAnchor: [0, -10]
});

const targetIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="red" stroke="white" stroke-width="2"/></svg>',
  iconSize: [20, 20],
  iconAnchor: [10, 10],
  popupAnchor: [0, -10]
});

interface MapViewProps {
  selectedScenario: ScenarioType;
}

const MapView: React.FC<MapViewProps> = ({ selectedScenario }) => {
  const [sites, setSites] = useState<Site[]>([]);
  const [targets, setTargets] = useState<Target[]>([]);

  // Fetch deployment sites once on component mount
  useEffect(() => {
    const fetchSites = async () => {
      const siteData = await getDeploymentSites();
      console.log('Sites fetched:', siteData);
      console.log('First site sample:', siteData[0]); // Check if is_qatar exists
      setSites(siteData);
    };
    fetchSites();
  }, [selectedScenario]); // Temporarily refetch on scenario change to get fresh data

  // Fetch scenario targets whenever the selected scenario changes
  useEffect(() => {
    console.log('useEffect triggered with selectedScenario:', selectedScenario);
    const fetchTargets = async () => {
      if (selectedScenario && typeof selectedScenario === 'number') {
        // Regular scenario: fetch specific targets
        console.log('Fetching targets for scenario:', selectedScenario);
        try {
          const targetData = await getScenarioTargets(selectedScenario);
          console.log('Targets fetched successfully:', targetData);
          setTargets(targetData);
        } catch (error) {
          console.error('Error fetching targets:', error);
          setTargets([]);
        }
      } else if (selectedScenario === 'robust') {
        // Robust scenario: fetch ALL targets
        console.log('Fetching all targets for robust scenario');
        try {
          const targetData = await getScenarioTargets('robust');
          console.log('All targets fetched successfully:', targetData);
          setTargets(targetData);
        } catch (error) {
          console.error('Error fetching all targets:', error);
          setTargets([]);
        }
      } else {
        console.log('No valid scenario selected, clearing targets');
        setTargets([]); // Clear targets when no valid scenario is selected
      }
    };
    fetchTargets();
  }, [selectedScenario]);

  return (
    <MapContainer center={[38.5, 35.5]} zoom={6} className="map-container">
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
      />
      
      {/* --- Render Deployment Sites (Blue) --- */}
      {sites.map(site => {
        // Qatar sites are inactive in scenario 3 (US-Israel Coalition)
        const isQatarInactive = site.is_qatar && selectedScenario === 3;
        const iconToUse = isQatarInactive ? qatarInactiveIcon : siteIcon;
        
        // Debug logging
        if (site.is_qatar) {
          console.log(`Qatar site ${site.name}: selectedScenario=${selectedScenario}, isQatarInactive=${isQatarInactive}`);
        }
        
        return (
          <Marker 
            key={`site-${site.site_id}`} 
            position={[site.y_coord, site.x_coord]}
            icon={iconToUse}
          >
            <Popup>
              <b>{site.name}</b><br />
              {isQatarInactive ? 'Deployment Site (INACTIVE)' : 'Deployment Site'}
            </Popup>
          </Marker>
        );
      })}

      {/* --- Render Scenario Targets (Red) --- */}
      {targets.map(target => (
        <Marker 
          key={`target-${target.target_id}`} 
          position={[target.y_coord, target.x_coord]}
          icon={targetIcon}
        >
          <Popup>
            <b>{target.name}</b><br />
            Target
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
};

export default MapView; 