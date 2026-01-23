import { z } from 'zod';
import { insertMissionSchema, insertSystemMetricSchema, insertContextItemSchema, missions, systemMetrics, contextItems } from './schema';

export const api = {
  missions: {
    list: {
      method: 'GET' as const,
      path: '/api/missions',
      responses: {
        200: z.array(z.custom<typeof missions.$inferSelect>()),
      },
    },
    create: {
      method: 'POST' as const,
      path: '/api/missions',
      input: insertMissionSchema,
      responses: {
        201: z.custom<typeof missions.$inferSelect>(),
      },
    },
    // Useful for the "Generate 100k tasks" simulation
    bulkCreate: {
      method: 'POST' as const,
      path: '/api/missions/bulk',
      input: z.object({ count: z.number().max(1000) }), // Limit for mock purposes
      responses: {
        201: z.object({ message: z.string(), count: z.number() }),
      },
    }
  },
  metrics: {
    list: {
      method: 'GET' as const,
      path: '/api/metrics',
      responses: {
        200: z.array(z.custom<typeof systemMetrics.$inferSelect>()),
      },
    },
    update: {
      method: 'POST' as const,
      path: '/api/metrics',
      input: insertSystemMetricSchema,
      responses: {
        200: z.custom<typeof systemMetrics.$inferSelect>(),
      },
    }
  },
  context: {
    list: {
      method: 'GET' as const,
      path: '/api/context',
      responses: {
        200: z.array(z.custom<typeof contextItems.$inferSelect>()),
      },
    }
  }
};

// Helper for frontend URL building
export function buildUrl(path: string, params?: Record<string, string | number>): string {
  let url = path;
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url = url.replace(`:${key}`, String(value));
    });
  }
  return url;
}
