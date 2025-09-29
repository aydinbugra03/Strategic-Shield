import axios from 'axios';
import { ScenarioType, AllocationResult, Site, Target } from '../App';

const API_BASE_URL = '/api';

export const runOptimization = async (scenario: ScenarioType): Promise<AllocationResult[] | null> => {
  try {
    const endpoint = scenario === 'robust' ? 'optimization/run/robust' : `optimization/run/${scenario}`;
    const response = await axios.post(`${API_BASE_URL}/${endpoint}`);
    
    if (response.status === 200 && response.data.allocations_found > 0) {
      // After running, fetch the results
      const results = await getOptimizationResults(scenario);
      return results;
    }
    return [];
  } catch (error) {
    console.error(`Error running optimization for scenario ${scenario}:`, error);
    throw error;
  }
};

export const getOptimizationResults = async (scenario: ScenarioType): Promise<AllocationResult[] | null> => {
  try {
    const endpoint = scenario === 'robust' ? 'optimization/results/robust' : `optimization/results/${scenario}`;
    const response = await axios.get(`${API_BASE_URL}/${endpoint}`);
    
    if (scenario === 'robust') {
      return response.data.results as AllocationResult[];
    }
    return response.data as AllocationResult[];
  } catch (error) {
    console.error(`Error fetching results for scenario ${scenario}:`, error);
    return null;
  }
};

export const getDeploymentSites = async (): Promise<Site[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/map/deployment-sites`);
    console.log("Fetched Sites Data:", response.data); // DEBUG: Gelen site verisini göster
    return response.data;
  } catch (error) {
    console.error("Error fetching deployment sites:", error);
    return [];
  }
};

export const getScenarioTargets = async (scenario: ScenarioType): Promise<Target[]> => {
  if (scenario === 'robust') {
    // For robust scenario, get all targets from all scenarios
    return getAllTargets();
  }
  
  try {
    const response = await axios.get(`${API_BASE_URL}/map/targets/${scenario}`);
    console.log("Fetched Targets Data:", response.data); // DEBUG: Gelen target verisini göster
    return response.data;
  } catch (error) {
    console.error(`Error fetching targets for scenario ${scenario}:`, error);
    return [];
  }
};

export const getAllTargets = async (): Promise<Target[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/map/targets/all`);
    console.log("Fetched All Targets Data:", response.data); // DEBUG: Gelen tüm target verisini göster
    return response.data;
  } catch (error) {
    console.error("Error fetching all targets:", error);
    return [];
  }
}; 