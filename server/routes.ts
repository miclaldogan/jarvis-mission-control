import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { api } from "@shared/routes";
import { z } from "zod";

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  
  // === Missions ===
  app.get(api.missions.list.path, async (req, res) => {
    const missions = await storage.getMissions();
    res.json(missions);
  });

  app.post(api.missions.create.path, async (req, res) => {
    const input = api.missions.create.input.parse(req.body);
    const mission = await storage.createMission(input);
    res.status(201).json(mission);
  });

  app.post(api.missions.bulkCreate.path, async (req, res) => {
    const { count } = api.missions.bulkCreate.input.parse(req.body);
    await storage.createMissionsBulk(count);
    res.status(201).json({ message: "Bulk generation initiated", count });
  });

  // === Metrics ===
  app.get(api.metrics.list.path, async (req, res) => {
    const metrics = await storage.getMetrics();
    res.json(metrics);
  });

  app.post(api.metrics.update.path, async (req, res) => {
    const input = api.metrics.update.input.parse(req.body);
    const metric = await storage.updateMetric(input);
    res.json(metric);
  });

  // === Context ===
  app.get(api.context.list.path, async (req, res) => {
    const context = await storage.getContextItems();
    res.json(context);
  });

  // === Seed Data ===
  await seedData();

  return httpServer;
}

async function seedData() {
  const existingMissions = await storage.getMissions();
  if (existingMissions.length === 0) {
    // Missions
    await storage.createMission({ title: "Initialize Core Systems", priority: "CRITICAL", category: "SYSTEM", status: "COMPLETED" });
    await storage.createMission({ title: "Analyze Network Traffic", priority: "HIGH", category: "RECON", status: "IN_PROGRESS" });
    await storage.createMission({ title: "Decrypt Intercepted Packets", priority: "NORMAL", category: "ENCRYPTION" });
    await storage.createMission({ title: "Update Firewall Rules", priority: "LOW", category: "SYSTEM" });

    // Metrics
    await storage.updateMetric({ name: "Compute Load", value: "2300 ms", status: "NOMINAL" });
    await storage.updateMetric({ name: "Cache Hit Rate", value: "94.2%", status: "HIT" });
    await storage.updateMetric({ name: "Active Nodes", value: "12/16", status: "WARNING" });

    // Context - Weather
    await storage.createContextItem({
      type: "WEATHER",
      title: "Local Conditions",
      content: "Heavy Rain / Storm Warning",
      metadata: { temp: "18°C", humidity: "82%" }
    });

    // Context - GitHub
    await storage.createContextItem({
      type: "GITHUB",
      title: "Issue Tracker",
      content: "3 Critical Vulnerabilities detected in dependencies",
      metadata: { repo: "mainframe-v2", stars: 1240 }
    });

    // Context - News
    await storage.createContextItem({
      type: "NEWS",
      title: "Tech Daily",
      content: "AI Quantum Superiority Reached in Sector 7",
      metadata: { source: "Reuters API" }
    });
  }
}
