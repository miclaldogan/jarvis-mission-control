import { db } from "./db";
import { 
  missions, systemMetrics, contextItems,
  type Mission, type InsertMission, 
  type SystemMetric, type InsertSystemMetric,
  type ContextItem, type InsertContextItem
} from "@shared/schema";

export interface IStorage {
  // Missions
  getMissions(): Promise<Mission[]>;
  createMission(mission: InsertMission): Promise<Mission>;
  createMissionsBulk(count: number): Promise<void>;
  
  // Metrics
  getMetrics(): Promise<SystemMetric[]>;
  updateMetric(metric: InsertSystemMetric): Promise<SystemMetric>;
  
  // Context
  getContextItems(): Promise<ContextItem[]>;
  createContextItem(item: InsertContextItem): Promise<ContextItem>;
}

export class MemStorage implements IStorage {
  private missions: Map<number, Mission>;
  private metrics: Map<number, SystemMetric>;
  private context: Map<number, ContextItem>;
  private currentId: number;

  constructor() {
    this.missions = new Map();
    this.metrics = new Map();
    this.context = new Map();
    this.currentId = 1;
  }

  async getMissions(): Promise<Mission[]> {
    return Array.from(this.missions.values()).sort((a, b) => b.id - a.id);
  }

  async createMission(insertMission: InsertMission): Promise<Mission> {
    const id = this.currentId++;
    const mission: Mission = { 
      ...insertMission, 
      id, 
      status: insertMission.status ?? "PENDING",
      isGlitched: insertMission.isGlitched ?? false,
      createdAt: new Date() 
    };
    this.missions.set(id, mission);
    return mission;
  }

  async createMissionsBulk(count: number): Promise<void> {
    const categories = ["SYSTEM", "RECON", "ENCRYPTION", "DATA_MINING"];
    const priorities = ["LOW", "NORMAL", "HIGH", "CRITICAL"];
    
    for (let i = 0; i < count; i++) {
      await this.createMission({
        title: `Operation ${Math.random().toString(36).substring(7).toUpperCase()}`,
        priority: priorities[Math.floor(Math.random() * priorities.length)] as any,
        category: categories[Math.floor(Math.random() * categories.length)],
        status: "PENDING"
      });
    }
  }

  async getMetrics(): Promise<SystemMetric[]> {
    return Array.from(this.metrics.values());
  }

  async updateMetric(insertMetric: InsertSystemMetric): Promise<SystemMetric> {
    // Upsert logic for mock storage (simulate updating existing metric by name)
    const existing = Array.from(this.metrics.values()).find(m => m.name === insertMetric.name);
    if (existing) {
      const updated = { ...existing, ...insertMetric, timestamp: new Date() };
      this.metrics.set(existing.id, updated);
      return updated;
    }

    const id = this.currentId++;
    const metric: SystemMetric = { ...insertMetric, id, timestamp: new Date() };
    this.metrics.set(id, metric);
    return metric;
  }

  async getContextItems(): Promise<ContextItem[]> {
    return Array.from(this.context.values());
  }

  async createContextItem(insertItem: InsertContextItem): Promise<ContextItem> {
    const id = this.currentId++;
    const item: ContextItem = { ...insertItem, id, createdAt: new Date() };
    this.context.set(id, item);
    return item;
  }
}

export const storage = new MemStorage();
