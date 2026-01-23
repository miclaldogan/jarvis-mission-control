import { pgTable, text, serial, integer, boolean, timestamp, jsonb } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// === TABLE DEFINITIONS ===

// Dashboard Missions/Tasks
export const missions = pgTable("missions", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  priority: text("priority", { enum: ["CRITICAL", "HIGH", "NORMAL", "LOW"] }).notNull(),
  status: text("status", { enum: ["PENDING", "IN_PROGRESS", "COMPLETED"] }).default("PENDING"),
  category: text("category").notNull(), // e.g., "SYSTEM", "RECON", "DATA"
  isGlitched: boolean("is_glitched").default(false), // For UI effects
  createdAt: timestamp("created_at").defaultNow(),
});

// System Metrics (Cache, Compute, etc.)
export const systemMetrics = pgTable("system_metrics", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(), // e.g., "Mainframe Compute", "Cache Hit Rate"
  value: text("value").notNull(), // e.g., "2300ms", "98%"
  status: text("status", { enum: ["NOMINAL", "WARNING", "CRITICAL", "HIT", "MISS"] }).notNull(),
  timestamp: timestamp("timestamp").defaultNow(),
});

// Context Data (Weather, News, Calendar)
export const contextItems = pgTable("context_items", {
  id: serial("id").primaryKey(),
  type: text("type", { enum: ["WEATHER", "CALENDAR", "NEWS", "GITHUB"] }).notNull(),
  title: text("title").notNull(),
  content: text("content").notNull(),
  metadata: jsonb("metadata"), // Flexible field for extra data (temp, url, etc.)
  createdAt: timestamp("created_at").defaultNow(),
});

// === SCHEMAS ===
export const insertMissionSchema = createInsertSchema(missions).omit({ id: true, createdAt: true });
export const insertSystemMetricSchema = createInsertSchema(systemMetrics).omit({ id: true, timestamp: true });
export const insertContextItemSchema = createInsertSchema(contextItems).omit({ id: true, createdAt: true });

// === TYPES ===
export type Mission = typeof missions.$inferSelect;
export type InsertMission = z.infer<typeof insertMissionSchema>;

export type SystemMetric = typeof systemMetrics.$inferSelect;
export type InsertSystemMetric = z.infer<typeof insertSystemMetricSchema>;

export type ContextItem = typeof contextItems.$inferSelect;
export type InsertContextItem = z.infer<typeof insertContextItemSchema>;
